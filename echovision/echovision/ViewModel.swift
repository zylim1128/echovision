//
//  ViewModel.swift
//  echovision
//
//  Created by Adina Tung on 2/23/25.
//
import Foundation
import CoreImage
import UIKit
import Observation
import AVFoundation


@Observable
class ViewModel: ObservableObject {
    private let nothingDetected: String = "No objects detected. No traffic signal detected."
    
    var currentFrame: CGImage?
    var detectedFrame: CGImage?
    var detectedText: String = "" {
        didSet {
            if detectedText != oldValue && !detectedText.contains(self.nothingDetected){  // Check if the new value is different
                speakDetectedText()
            }
        }
    }
    
    private let ttsManager = TextToSpeechManager()
    
    // Update from server response
    func updateFromServerResponse(_ response: ServerResponse?) {
        guard let response = response else { return }
        self.detectedFrame = response.filename
        self.detectedText = response.result
    }
    
    func updateFromCaptureSession(_ frame: CGImage) {
        self.currentFrame = frame
    }
    
    private func speakDetectedText() {
        guard !detectedText.isEmpty else { return }
        ttsManager.speak(detectedText)
    }
}


