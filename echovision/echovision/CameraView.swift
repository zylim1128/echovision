//
//  CameraView.swift
//  echovision
//
//  Created by Adina Tung on 2/23/25.
//
import SwiftUI

struct CameraView: View {
    @Binding var rtImage: CGImage?
    @Binding var filename: CGImage?
    
    var body: some View {
        VStack {
            GeometryReader { geometry in
                if let image = rtImage {
                    ZStack {
                        Image(decorative: image, scale: 1)
                            .resizable()
                            .aspectRatio(contentMode: .fill) // Ensures the image fills the frame
                            .frame(width: geometry.size.width * 0.9,
                                   height: geometry.size.height * 0.9)
                            .padding(geometry.size.width * 0.05)
                    }
                } else {
                    ContentUnavailableView("No camera feed", systemImage: "xmark.circle.fill")
                        .frame(width: geometry.size.width * 0.9,
                               height: geometry.size.height * 0.9)
                }
            }
            
            GeometryReader { geometry in
                if let image = filename {
                    ZStack {
                        Image(decorative: image, scale: 1)
                            .resizable()
                            .aspectRatio(contentMode: .fill) // Ensures the image fills the frame
                            .frame(width: geometry.size.width * 0.9,
                                   height: geometry.size.height * 0.9)
                            .padding(geometry.size.width * 0.05)
                    }
                } else {
                    ContentUnavailableView("No camera feed", systemImage: "xmark.circle.fill")
                        .frame(width: geometry.size.width * 0.9,
                               height: geometry.size.height * 0.9)
                }
            }
            
        }
    }
    
}
