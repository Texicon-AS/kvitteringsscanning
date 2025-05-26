// `self` is a type containing an sqlx database connection pool
async fn scan_receipt(
    &self,
    request: Request<scan_receipt::Request>,
) -> Result<Response<scan_receipt::Response>, Status> {
    let body = request.into_inner().items;

    // map to model type
    let items: Box<_> = body.into_iter().map(ReceiptEntry::from_proto).collect();

    // predictions from the Python micro-service
    let hints = product_search::predictive(self.predictions.clone(), &items).await;

    assert_eq!(items.len(), hints.len()); // sanity check

    let corrections = product_search::receipt_corrections(&self.db, &items)
        .await
        .or_msg("Failed to fetch by receipt correction")?;

    assert_eq!(corrections.len(), items.len());

    let substring = product_search::substring(&self.db, &items, &hints, &corrections)
        .await
        .or_msg("failed substring search")?;

    let receipt_entries = std::iter::zip(corrections, substring)
        .map(|(mut options, b)| {
            // grab options returned by substring search
            // until there are at most 32 options overall per item from the input
            let max_from_b = b.len().min(32 - options.len());
            options.extend_from_slice(&b[..max_from_b]);
            FuzzyMatchOptions { options }
        })
        .collect();

    Ok(Response::new(scan_receipt::Response { receipt_entries }))
}