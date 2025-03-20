//
//  UIImage+Extensions.swift
//  echovision
//
//  Created by Adina Tung on 3/12/25.
//

import UIKit

// Extend UIImage with a method to convert it to CGImage
extension UIImage {
    func toCGImage() -> CGImage? {
        return self.cgImage
    }
}
