import { ObjectCannedACL, PutObjectCommand } from "@aws-sdk/client-s3";
import { randomUUID } from "crypto";
import { Router } from "express";
import multer from "multer";
import OpenAI from "openai";
import sharp from "sharp";
import { s3Client } from "../storage/s3client";
const vision = require('@google-cloud/vision');
//import vision from '@google-cloud/vision';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Initialize Google Cloud Vision client with credentials from environment variables
const visionClient = new vision.ImageAnnotatorClient({
  credentials: JSON.parse(process.env.GOOGLE_APPLICATION_CREDENTIALS_CONTENT)
});

const ocrRouter = Router({});
const upload = multer({
  storage: multer.memoryStorage(),
});

ocrRouter.post("/", upload.single("file"), async (req, res) => {
  console.log('Starting OCR process for new image upload');
  const image = req.file;

  try {
    console.log('Optimizing image for OCR processing...');
    // Optimize image for OCR
    const optimizedImageBuffer = await sharp(image.buffer)
      .grayscale()
      .resize({
        width: 800,
        height: 800,
        fit: 'inside',
      })
      .normalise()
      .sharpen()
      .resize({
        width: 1024,
        height: 1024,

      })
      .toBuffer();
    console.log('Image optimization complete');

    // Get text from Google Cloud Vision
    console.log('Sending image to Google Cloud Vision for text detection...');
    const [result] = await visionClient.textDetection({
      image: { content: optimizedImageBuffer }
    });
    const detections = JSON.stringify(result.textAnnotations);
    console.log('Text detection complete. Characters detected:', detections.length);
    console.log('Text detected:', detections);

    // Use the extracted text in the ChatGPT prompt
    console.log('Analyzing text with GPT-4...');
    const response = await scanReceipt(detections);

    const items = JSON.parse(
      response.choices[0].message.tool_calls[0].function.arguments
    );
    console.log('GPT-4 analysis complete. Items found:', items.items.length);
    console.log('Items:', items);
    
    // Send response immediately
    res.status(200).json(items);

    // Upload to S3 asynchronously after sending response
    const uuid = randomUUID();
    const date = new Date().toISOString();
    const fileKey = `foodmanager/ocr/${date}_${uuid}.png`;

    console.log('Uploading image to S3...', { fileKey });
    const uploadCommand = new PutObjectCommand({
      Bucket: process.env.SPACES_BUCKET_NAME,
      Key: fileKey,
      Body: optimizedImageBuffer,
      ACL: ObjectCannedACL.public_read,
    });

    // Fire and forget S3 upload
    s3Client.send(uploadCommand)
      .then(() => console.log('S3 upload complete:', fileKey))
      .catch(error => {
        console.error('Failed to upload image to S3:', error);
      });

  } catch (error) {
    console.error('Error in OCR process:', error);
    res.status(500).json({ error: 'Failed to process image' });
  }
});

async function scanReceipt(extractedText: string) {
  console.log('Starting GPT analysis with text length:', extractedText.length);
  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      tool_choice: "required",
      messages: [
        {
          role: "user",
          content: [
            {
              type: "text",
              text: `Analyze this receipt text and extract the items. The text was extracted using OCR and might contain some errors. The language is primarily in Norwegian, but there may be some English words. Extract only things that can be used in a recipe or is edible. Include the exact item name as written, but only the left side part of the line (no price or amount unless it's part of the item name). For identical items, sum up the amount. For weight-priced items, include the amount in grams. For non-weight items, include the count. Ignore items with negative prices. Here's the extracted text:\n\n${extractedText}`,
            }
          ],
        },
      ],
      temperature: 0.05,
      max_tokens: 16383,
      top_p: 1,
      frequency_penalty: 0,
      presence_penalty: 0,
      tools: [
        {
          type: "function",
          function: {
            name: "extract_receipt_items",
            parameters: {
              type: "object",
              required: ["items"],
              properties: {
                items: {
                  type: "array",
                  items: {
                    type: "object",
                    required: ["amount", "name", "is_priced_by_weight"],
                    properties: {
                      name: {
                        type: "string",
                        description: "The name of the item. Include the entire text line of the product name, but only the product name. Not price. Only include the amount if it is present on the left side of the line, next to the name.",
                      },
                      amount: {
                        type: "integer",
                        description: "The amount of the item. If the item is priced by weight, this is the weight in grams. If the item is not priced by weight, this is the count. Make sure that if the amount in one pack is given, such as 6pk, count that as one item, not 6. If there are entries for the same thing but with different pack amounts, don't sum them up. For weight-priced items with decimal numbers in kilograms, convert to grams.",
                      },
                      is_priced_by_weight: {
                        type: "boolean",
                        description: "Whether the item is priced by weight or not. True if the receipt has a [price] kr X [amount] directly beneath or next to the name.",
                      },
                    },
                  },
                },
              },
            },
            description: "Extracts items from a receipt text.",
          },
        },
      ],
    });
    console.log('GPT analysis completed successfully');
    return response;
  } catch (error) {
    console.error('Error during GPT analysis:', error);
    throw error;
  }
}

export default ocrRouter;
