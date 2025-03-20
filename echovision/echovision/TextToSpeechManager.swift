//
//  TextToSpeechManager.swift
//  echovision
//
//  Created by Adina Tung on 3/19/25.
//

import AVFoundation

class TextToSpeechManager {
    private let synthesizer = AVSpeechSynthesizer()

    func speak(_ text: String, _ rate: Float = 0.6) {
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = AVSpeechSynthesisVoice(language: "en-US")
        utterance.rate = rate
        
        synthesizer.speak(utterance)
    }
}
