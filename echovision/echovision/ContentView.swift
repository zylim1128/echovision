import SwiftUI

struct ContentView: View {
    @State private var isActive = false
    @State private var isDevMode = true
    
    @StateObject private var viewModel = ViewModel()
    @StateObject private var imageCaptureManager = ImageCaptureManager()


    var body: some View {
        
        VStack {
            Spacer()
            
            HStack {
                // Status Text
                Text(isActive ? "✅ Active" : "🚫 Idle")
                    .font(.title)
                    .fontWeight(.bold)
                    .foregroundColor(.white)

//                Spacer()

                
                // Start/Stop Button
                Button(action: {
                    isActive.toggle()
                    
                    if isActive {
                        imageCaptureManager.startCapturing()
                    } else {
                        imageCaptureManager.stopCapturing()
                    }
                }) {
                    Text(isActive ? "Stop" : "Start")
                        .font(.title)
                        .fontWeight(.bold)
                        .frame(width: 100, height: 100)
                        .background(isActive ? Color.white: Color.gray)
                        .foregroundColor(isActive ? .black : .white)
                        .clipShape(Circle())
                        .overlay(Circle().stroke(Color.black, lineWidth: 2))
                }
            }


//            Spacer()
            
            
            // Placeholder for Camera Preview (Static Box Instead)
            if isActive && isDevMode {
                ZStack {
                    // Use the video preview layer in the background
                    CameraView(rtImage: $viewModel.currentFrame, filename: $viewModel.detectedFrame)
                        .clipShape(RoundedRectangle(cornerRadius: 20)) // Apply rounded corners
                        .overlay(
                            RoundedRectangle(cornerRadius: 20)
                                .stroke(Color.gray, lineWidth: 3) // Optional border for visibility
                        )
                        .shadow(radius: 10) // Optional shadow for better contrast
                }

                
                Text(viewModel.detectedText)
                    .font(.body)
                    .foregroundColor(.gray)
                    .padding(.top, 8) // Space between rectangle and text
                    .multilineTextAlignment(.leading)
                
                
//                // Display Detected Text Below the Image
//                Text(result)
//                    .font(.headline)
//                    .padding()
                
            }

            Spacer()

            // Dev Mode Toggle
            Toggle("dev mode", isOn: $isDevMode)
                .padding()
        }
        .padding()
        .onAppear() {
            // Attach ViewModel after initialization
            imageCaptureManager.attachViewModel(viewModel: viewModel)
            
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}


