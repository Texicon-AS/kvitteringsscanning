use crate::prediction;
use crate::proto::inventory::scan_receipt::{ItemOption, OcrItem};

pub struct ReceiptEntry {
    pub text: String,
    pub amount: u32,
    pub _unit: String,
    pub multiply_with_bulk: bool,
}

impl ReceiptEntry {
    pub fn from_proto(dto: OcrItem) -> Self {
        Self {
            text: dto.name_query,
            amount: u32::try_from(dto.amount).unwrap(),
            _unit: dto.unit,
            multiply_with_bulk: !dto.is_priced_by_weight,
        }
    }
}

pub async fn receipt_corrections(
    pool: &sqlx::PgPool,
    values: &[ReceiptEntry],
) -> Result<Vec<Vec<ItemOption>>, sqlx::Error> {
    let mut results = Vec::with_capacity(values.len());

    for ReceiptEntry {
        text,
        amount,
        multiply_with_bulk,
        ..
    } in values
    {
        let amount = *amount;

        let output = sqlx::query!(
            r"
            SELECT *
            FROM receipt_correction
                JOIN product p on p.id = receipt_correction.product_id
            WHERE receipt_text = $1
            ORDER BY count DESC, random()
            LIMIT 3
            ",
            text.to_lowercase()
        )
        .fetch_all(pool)
        .await?;

        let mapped = output
            .into_iter()
            .map(|row| ItemOption {
                distance: 0,
                product_id: row.product_id.to_string(),
                product_name: row.name,
                unit: row.unit.unwrap_or("piece".to_owned()),
                amount: if *multiply_with_bulk {
                    row.bulk_product_amount
                        .map(|a| u32::try_from(a).unwrap() * amount)
                        .unwrap_or(amount)
                } else {
                    amount
                },
            })
            .collect();

        results.push(mapped);
    }

    Ok(results)
}

pub async fn substring(
    pool: &sqlx::PgPool,
    items: &[ReceiptEntry],
    hints: &[Option<prediction::Output>],
    corrections: &[Vec<ItemOption>],
) -> Result<Vec<Vec<ItemOption>>, sqlx::Error> {
    // split up queries into words, and lowercase them while we're at it
    let (mut indices, mut keywords) = (Vec::new(), Vec::new());

    // add hints and exclude items found in receipt corrections
    let to_check = items
        .iter()
        .zip(hints)
        .enumerate()
        .filter(|(idx, _)| corrections[*idx].len() < 3);

    let mut push_words = |i, text: &str| {
        for word in text.split_whitespace() {
            // save the index of the item to which each keyword belongs, to be used later
            indices.push(i);
            keywords.push(word.to_lowercase());
        }
    };

    for (i, (item, hint)) in to_check {
        // database accepts an i32, not a usize
        let i = i32::try_from(i).unwrap();
        // add the name given by the prediction service, if it was found
        if let Some(h) = hint {
            push_words(i, &h.name);
        }
        push_words(i, &item.text);
    }

    substring_inner(&indices, &keywords, items, pool).await
}

async fn substring_inner(
    indices: &[i32],
    keywords: &[String],
    items: &[ReceiptEntry],
    pool: &sqlx::PgPool,
) -> Result<Vec<Vec<ItemOption>>, sqlx::Error> {
    let output = sqlx::query!(
        r#"
        WITH input (idx, key) AS (
            SELECT *
            FROM unnest($1::int[], $2::text[])
        ), counted AS (
            SELECT i.idx, p.id, p.name, p.unit, p.bulk_product_amount,
                   Row_Number() OVER (
                       PARTITION BY i.idx
                       ORDER BY i.idx, Count(p.id) DESC, p.name_length
                   ) AS rank
            FROM product p, input i
            WHERE Char_Length(i.key) <= p.name_length
                AND Position(i.key IN p.name_lowercased) > 0
            GROUP BY i.idx, p.id
        )
        SELECT c.idx, c.name, c.id, c.unit, c.bulk_product_amount
        FROM counted c
        WHERE c.rank <= 25 "#,
        indices,
        keywords
    )
    .fetch_all(pool)
    .await?;

    // pre-allocating the output vectors greatly simplifies the loop
    let mut receipt_entries: Vec<_> = std::iter::repeat_with(Vec::new).take(items.len()).collect();

    // fit rows into the output types
    for row in output {
        let i = usize::try_from(row.idx.unwrap()).unwrap();

        let mut amount = items[i].amount;

        if items[i].multiply_with_bulk {
            let bulk_amount = row.bulk_product_amount.unwrap_or(1);

            amount = amount
                .checked_mul(u32::try_from(bulk_amount).unwrap())
                .unwrap_or(amount);
        };

        // use the index saved earlier to find each item's place in the output
        receipt_entries[i].push(ItemOption {
            product_name: row.name,
            product_id: row.id.to_string(),
            amount,
            unit: row.unit.unwrap_or("piece".to_owned()),
            distance: 0,
        });
    }

    Ok(receipt_entries)
}

pub async fn predictive(
    mut client: prediction::Client,
    ocr: &[ReceiptEntry],
) -> Vec<Option<prediction::Output>> {
    // the prediction service requires that each word has an uppercase letter at the beginning
    let items = ocr.iter().map(|v| capitalize(&v.text)).collect();

    log::info!("Trying to predict: {:?}", &items);

    client.predict(items).await.unwrap()
}

fn capitalize(arg: &str) -> String {
    let mut out = Vec::new();
    for word in arg.split_whitespace() {
        let capped = word[..1].to_uppercase() + &word[1..].to_lowercase();

        out.push(capped);
    }
    out.join(" ")
}
