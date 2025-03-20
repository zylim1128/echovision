//
//  ImageCaptureManager.swift
//  echovision
//
//  Created by Adina Tung on 3/12/25.
//
import Foundation
import CoreImage
import AVFoundation
import UIKit

class ImageCaptureManager: NSObject, ObservableObject {
    let serverIP = "169.254.112.140"
    let serverPort = "52252"
    let CAPTURE_INTERVAL = 0.8
    
    private let cameraManager = CameraManager()
    private var timer: Timer?

    private var latestFrame: CGImage? // Store the latest frame

    // Binding to update the UI with the annotated image
//    @Published var annotatedImage: CGImage?

    // Add ViewModel as a dependency (injected at initialization)
    private var viewModel: ViewModel?

    
    func attachViewModel(viewModel: ViewModel) {
        self.viewModel = viewModel
    }
    
    // Start Capturing
    func startCapturing() {
        Task {
            await handleCameraPreviews()
        }

        // Start a timer to send frames every 3 seconds
        timer = Timer.scheduledTimer(timeInterval: CAPTURE_INTERVAL, target: self, selector: #selector(captureAndSendFrame), userInfo: nil, repeats: true)
    }

    // Stop Capturing
    func stopCapturing() {
        timer?.invalidate()
        timer = nil
    }
    

    private func handleCameraPreviews() async {
        Task {
            for await frame in cameraManager.previewStream {
                latestFrame = frame
            }
        }
    }

    @objc private func captureAndSendFrame() {
        guard let frame = latestFrame else { return } // Use the stored frame
        
        sendFrameToUI(frame)
        
        sendFrameToServer(frame) { result in
            switch result {
            case .success(let responseData):
//                print("Server response received: \(responseData)")
                // Now process the response data and update ViewModel
                self.fetchServerData(responseData) // 🔷
            case .failure(let error):
                print("Error sending frame: \(error.localizedDescription)")
            }
        }
    }
    
    
    func loadFileData(filename: String) -> Data? {
        let fileManager = FileManager.default
        let currentPath = fileManager.currentDirectoryPath
        let fileURL = URL(fileURLWithPath: currentPath).appendingPathComponent(filename)
        
        do {
            return try Data(contentsOf: fileURL)
        } catch {
            print("Error loading file: \(error)")
            return nil
        }
    }
    
    private func sendFrameToUI(_ frame: CGImage) {
        // Call updateFromServerResponse to update the ViewModel
        DispatchQueue.main.async {
            self.viewModel?.updateFromCaptureSession(frame)
        }
    }
    
    private func sendFrameToServer(_ frame: CGImage, completion: @escaping (Result<Data, Error>) -> Void) {
        // Convert CGImage to Data (PNG)
        guard let pngData = frame.toPNGData() else {
            completion(.failure(NSError(domain: "ConversionError", code: -1, userInfo: [NSLocalizedDescriptionKey: "Failed to convert image"])))
            return
        }
    
        
        let serverURL = URL(string: "http://\(serverIP):\(serverPort)/detect/")!

        var request = URLRequest(url: serverURL)
        
        let boundary = UUID().uuidString

        
       request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        request.httpMethod = "POST"
//        request.setValue("image/png", forHTTPHeaderField: "Content-Type")
        
        // Get the current date and time
        let currentDate = Date()

        // Create a DateFormatter to format the date
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "MMdd_HHmmss"  // yyyy You can customize the format as needed
        let formattedDate = dateFormatter.string(from: currentDate)
        
        var body = Data()
        let filename = "image_\(formattedDate).png"
        let fieldName = "file"

        // Append multipart headers
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"\(fieldName)\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/png\r\n\r\n".data(using: .utf8)!)
        body.append(pngData)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)

        request.httpBody = body

        
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                print("FAILURE")
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse else {
                // If the response is not an HTTP URL response
                completion(.failure(NSError(domain: "ServerError", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid server response"])))
                print("INVALID SERVER RESPONSE")
                if let error = error {
                    print("Error: \(error.localizedDescription)")  // Print the error message
                }
                return
            }

            if httpResponse.statusCode != 200 {
                // If the status code is not 200 (OK)
                let statusCode = httpResponse.statusCode
                let statusMessage = HTTPURLResponse.localizedString(forStatusCode: statusCode)
                completion(.failure(NSError(domain: "ServerError", code: statusCode, userInfo: [NSLocalizedDescriptionKey: "Server returned an error: \(statusMessage)"])))
                
                print("Server returned error. Status code: \(statusCode), Message: \(statusMessage)")
                return
            }
            

            guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200, let responseData = data else {
                completion(.failure(NSError(domain: "ServerError", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid server response"])))
                print("INVALID SERVER RESPONSE")
                
                
                return
            }

            completion(.success(responseData)) // Pass response data to the completion
        }
        task.resume()
    }

    // Fetch server data and update ViewModel
    private func fetchServerData(_ data: Data) {
        do {
            //            if let jsonString = String(data: data, encoding: .utf8) {
            //                print("Raw JSON Data: \(jsonString)")
            //            }
            
            // Decode JSON response into ServerResponse
            let decodedResponse = try JSONDecoder().decode(ServerResponse.self, from: data)

            // Call updateFromServerResponse to update the ViewModel
            DispatchQueue.main.async {
                self.viewModel?.updateFromServerResponse(decodedResponse)
            }

        } catch {
            print("Failed to decode server response: \(error)")
        }
    }
}

// **Helper Extension to Convert CGImage to JPEG Data**
extension CGImage {
    func toPNGData() -> Data? {
        let uiImage = UIImage(cgImage: self)
        return uiImage.pngData() // Convert UIImage to PNG
    }
}


//--------capture and send frame triggered
//Server response received: 75 bytes
//Failed to decode server response: typeMismatch(Swift.String, Swift.DecodingError.Context(codingPath: [CodingKeys(stringValue: "filename", intValue: nil)], debugDescription: "Expected to decode String but found a dictionary instead.", underlyingError: nil))
