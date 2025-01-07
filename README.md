# Talking Alarm Clock for Raspberry Pi

This project is a simple voice assistant application developed by Kai Zuberbühler as part of the CDS 205 module for the B.Sc. Artificial Intelligence in Software Engineering program at the University of Applied Sciences of the Grisons. The application is designed to run on a Raspberry Pi with a WM8960 sound card HAT and leverages various AI services to provide a seamless voice interaction experience.

## Features

- **Modular Design:** The application is built using base classes for each component, allowing for easy integration of alternative service providers.
- **Real-time Interaction:** Provides real-time voice interaction using ASR (Automatic Speech Recognition), LMs (Language Models) and TTS (Text-to-Speech).
- **Function Management:** Supports several functions such as setting an alarm, which can be managed through voice commands in natural language.

## Components

### ASR (Automatic Speech Recognition)

- **Base Class:** `BaseASRClient`
- **Current Implementation:** `FalAiASRClient`
- **Description:** The ASR component is responsible for transcribing audio input into text. The current implementation uses the Fal AI service, but it can be easily replaced with another ASR service by implementing the `BaseASRClient` interface.

### TTS (Text-to-Speech)

- **Base Class:** `BaseTTSClient`
- **Current Implementation:** `ElevenLabsTTSClient`
- **Description:** The TTS component converts text responses into audio. The current implementation uses the Eleven Labs service, but it can be swapped with another TTS service by implementing the `BaseTTSClient` interface.

### LM (Language Model)

- **Base Class:** `BaseLMClient`
- **Current Implementation:** `CerebrasLMClient`
- **Description:** This component uses a language model to generate a response based on a given user-assistant interaction and a system prompt.

### Chat

- **Class:** `Chat`
- **Description:** Manages the conversation with the user, utilizing a language model to generate responses. It also handles function calls based on user requests.

### Functions

- **Class:** `Functions`
- **Description:** This component manages the execution of various functions that the voice assistant can perform, such as enabling or disabling alarms and announcing the time. The `Functions` class implements the `FunctionInterface` and provides a structured way to define and call functions based on user requests.
- **Function Management:** The `Functions` class contains a list of available functions, each defined with a reference, description, and parameters. It parses user requests to determine which functions to call and executes them accordingly.
- **YAML Parsing:** The component uses YAML to parse and manage function calls, ensuring that requests are formatted correctly and that the appropriate functions are executed.
- **Extensibility:** New functions can be added by defining them in the `Functions` class, making it easy to extend the capabilities of the voice assistant with minimal changes to the existing code.

### Audio Recorder

- **Base Class:** `BaseAudioRecorder`
- **Current Implementations:** `PyAudioButtonAudioRecorder` (default, for Raspberry Pi) and `PyAudioKeyboardAudioRecorder` (for testing using keyboard instead of button)
- **Description:** Captures audio input from the user. The current implementation uses PyAudio and can be replaced with another audio recording method by implementing the `BaseAudioRecorder` interface.

## Installation

To set up the application on your Raspberry Pi, follow these steps:

1. **Clone the Repository:**

   Begin by cloning the project repository to your local machine:

   ```bash
   git clone https://github.com/k-zubi/cds-205-raspberry-pi
   cd cds-205-raspberry-pi
   ```

2. **Set Up Python Environment:**

   Ensure you have Python installed on your Raspberry Pi. It's recommended to use a virtual environment to manage dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Install WM8960 Sound Card Drivers:**

   For using the WM8960 sound card with your Raspberry Pi, you need to install the appropriate drivers. Follow the steps in the official installation guide at https://www.waveshare.com/wiki/WM8960_Audio_HAT#Install_Driver.

4. **Install MPV and LGPIO:**

   The application uses MPV to play audio streams. Install it using the following command:

   ```bash
   sudo apt-get install mpv
   ```

5. **Setup API Keys:**

    The application uses the AI cloud services from Fal.ai, Cerebras and ElevenLabs. You need an API key from each of these services and then create a `.env` file in the project root directory containing the keys:
    ```
    CEREBRAS_API_KEY=
    FAL_KEY=
    ELEVENLABS_API_KEY=
    ```

6. **Run the Application:**

   Once all dependencies and drivers are installed, you can run the application:

   ```bash
   source .venv/bin/activate
   python main.py
   ```

## License

This project is licensed under the MIT License.
