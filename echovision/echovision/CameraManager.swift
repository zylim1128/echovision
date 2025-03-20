//
//  CameraManager.swift
//  echovision
//
//  Created by Adina Tung on 2/23/25.
//
import Foundation
import AVFoundation
import UIKit

class CameraManager: NSObject {
    // 1. performs real-time capture and adds appropriate inputs and outputs
    private let captureSession = AVCaptureSession()
    // 2. describes the media input from a capture device to a capture session
    private var deviceInput: AVCaptureDeviceInput?
    // 3. used to have access to video frames for processing
    private var videoOutput: AVCaptureVideoDataOutput?
    // 4. represents the hardware or virtual capture device that can provide one or more streams of media of a particular type
    private let systemPreferredCamera = AVCaptureDevice.default(for: .video)
    // 5. the queue on which the AVCaptureVideoDataOutputSampleBufferDelegate callbacks should be invoked.
    // It is mandatory to use a serial dispatch queue to guarantee that video frames will be delivered in order.
    private var sessionQueue = DispatchQueue(label: "video.preview.session")
    private var videoConnection: AVCaptureConnection?
//    private var previewLayer: AVCaptureVideoPreviewLayer? // diamond
    
    // Callback to pass the preview layer to the view controller
    var onPreviewLayerReady: ((AVCaptureVideoPreviewLayer) -> Void)?
    
    private var isAuthorized: Bool {
        get async {
            let status = AVCaptureDevice.authorizationStatus(for: .video)
            
            // Determine if the user previously authorized camera access.
            var isAuthorized = status == .authorized
            
            // If the system hasn't determined the user's authorization status,
            // explicitly prompt them for approval.
            if status == .notDetermined {
                isAuthorized = await AVCaptureDevice.requestAccess(for: .video)
            }
            
            return isAuthorized
        }
    }
    
    private var addToPreviewStream: ((CGImage) -> Void)?
    
    lazy var previewStream: AsyncStream<CGImage> = {
        // lazy variables init are delayed until it's used
        // async stream creates an asynchronous sequenc
        AsyncStream { continuation in
            addToPreviewStream = { cgImage in
                continuation.yield(cgImage)
            }
        }
    }()
    
    
    // 1.
    override init() {
        super.init()
        
        Task {
            // confugures and starts the `AVCaptureSession` at the same time
            await configureSession()
            await startSession()
        }
    }
    
    // 2. Inits all properties and defines the "buffer delegate"
    private func configureSession() async {
        // 1.
        guard await isAuthorized,
              let systemPreferredCamera,
              let deviceInput = try? AVCaptureDeviceInput(device: systemPreferredCamera)
        else { return }
        
        // 2.
        captureSession.beginConfiguration()
        
        // 3.
        defer {
            self.captureSession.commitConfiguration()
        }
        
        // 4.
        let videoOutput = AVCaptureVideoDataOutput()
        videoOutput.setSampleBufferDelegate(self, queue: sessionQueue)
        
        // 5.
        guard captureSession.canAddInput(deviceInput) else {
            print("Unable to add device input to capture session.")
            return
        }
        
        // 6.
        guard captureSession.canAddOutput(videoOutput) else {
            print("Unable to add video output to capture session.")
            return
        }
        
        // 7.
        captureSession.addInput(deviceInput)
        captureSession.addOutput(videoOutput)
        
        
        // 8. Initialize preview layer
        // Initialize preview layer
//        previewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
//        previewLayer?.videoGravity = .resizeAspectFill
//
//        // Notify the view controller that the preview layer is ready
//        if let previewLayer = previewLayer {
//            onPreviewLayerReady?(previewLayer)
//        }
        
           
        // Get the video connection
//        if let connection = videoOutput.connection(with: .video) {
//            videoConnection = connection
//            
//            // Apply a 90-degree rotation to make the video landscape-right
//            // Rotate by 90 degrees to force landscape-right orientation
//            applyRotationBasedOnDeviceOrientation()
//        }
    }
    
    // Apply rotation based on device's physical orientation
    private func applyRotationBasedOnDeviceOrientation() {
        guard let connection = videoConnection else { return }
        connection.videoRotationAngle = -(.pi / 2)
        
        // Get the device's physical orientation
//        let deviceOrientation = UIDevice.current.orientation
        
//        // Map the device orientation to the required rotation angle for portrait-right
//        var rotationAngle: CGFloat = 0.0
//        
//        switch deviceOrientation {
//        case .portrait:
//            rotationAngle = 0 // No rotation for portrait
//        case .landscapeLeft:
//            rotationAngle = .pi / 2  // 90 degrees for landscape-left
//        case .landscapeRight:
//            rotationAngle = -(.pi / 2)  // -90 degrees for landscape-right
//        case .portraitUpsideDown:
//            rotationAngle = .pi  // 180 degrees for upside down
//        default:
//            rotationAngle = 0  // Default: no rotation if the device orientation is unknown
//        }
//        
//        // Apply the calculated rotation angle to the video connection
//        connection.videoRotationAngle = rotationAngle + .pi / 2
        
    }

    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
    
    // 3. Starts the camera session
    private func startSession() async {
        /// Checking authorization
        guard await isAuthorized,
              let _ = systemPreferredCamera else { return }
        /// Start the capture session flow of data
        captureSession.startRunning()
    }
    
    
}

extension CameraManager: AVCaptureVideoDataOutputSampleBufferDelegate {
    
    func captureOutput(_ output: AVCaptureOutput,
                       didOutput sampleBuffer: CMSampleBuffer,
                       from connection: AVCaptureConnection) {
        guard let currentFrame = sampleBuffer.cgImage else { return }
        addToPreviewStream?(currentFrame)
    }
    
}
