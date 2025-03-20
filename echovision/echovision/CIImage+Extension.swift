//
//  CIImage+Extension.swift
//  echovision
//
//  Created by Adina Tung on 2/23/25.
//
import CoreImage

// Converts a CIImage to a CGImage
extension CIImage {
    var cgImage: CGImage? {
        let ciContext = CIContext()
        
        guard let cgImage = ciContext.createCGImage(self, from: self.extent) else {
            return nil
        }
        
        return cgImage
    }
    
}

