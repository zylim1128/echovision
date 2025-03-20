//
//  ServerModel.swift
//  echovision
//
//  Created by Adina Tung on 3/12/25.
//
import Foundation
import UIKit


struct ServerResponse: Decodable {
    let filename: CGImage?
    let result: String

    private enum CodingKeys: String, CodingKey {
        case imageBase64 = "filename"
        case result
    }

                
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        let base64String = try container.decode(String.self, forKey: .imageBase64)
        
        
        // Convert Base64 string to Data
        if let imageData = Data(base64Encoded: base64String),
            let uiImage = UIImage(data: imageData),
                let cgImage = uiImage.cgImage {
                    self.filename = cgImage
                
        } else {
            self.filename = nil
        }
        
        // Decode the result field (text)
        self.result = try container.decode(String.self, forKey: .result)
    }
}


//--------capture and send frame triggered
//Server response received: 75 bytes
//Failed to decode server response: typeMismatch(Swift.String, Swift.DecodingError.Context(codingPath: [CodingKeys(stringValue: "filename", intValue: nil)], debugDescription: "Expected to decode String but found a dictionary instead.", underlyingError: nil))
//--------capture and send frame triggered



