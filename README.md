# Vana Satya Proof of Contribution - dFusion Private Social Lens

This repository serves as a template for creating a [proof of contribution](https://docs.vana.org/vana/core-concepts/key-elements/proof-of-contribution) tasks using Python. It is executed on Vana's Satya Network, a group of highly confidential and secure compute nodes that can validate data without revealing its contents to the node operator.

## Overview

This template provides a basic structure for building proof tasks that:

1. Read input files from the `/input` directory.
2. Process the data securely, running any necessary validations to prove the data authentic, unique, high quality, etc.
3. Write proof results to the `/output/results.json` file in the following format:

```json
{
  "dlp_id": 1234, // DLP ID is found in the Root Network contract after the DLP is registered
  "valid": false, // A single boolean to summarize if the file is considered valid in this DLP
  "score": 0.7614457831325301, // A score between 0 and 1 for the file, used to determine how valuable the file is. This can be an aggregation of the individual scores below.
  "authenticity": 1.0, // A score between 0 and 1 to rate if the file has been tampered with
  "ownership": 1.0, // A score between 0 and 1 to verify the ownership of the file
  "quality": 0.6024096385542169, // A score between 0 and 1 to show the quality of the file
  "uniqueness": 0, // A score between 0 and 1 to show unique the file is, compared to others in the DLP
  "attributes": { // Custom attributes that can be added to the proof to provide extra context about the encrypted file
    "total_score": 0.5,
    "score_threshold": 0.83,
    "email_verified": true
  }
}
```

The project is designed to work with Intel TDX (Trust Domain Extensions), providing hardware-level isolation and security guarantees for confidential computing workloads.

## Project Structure

- `psl_proof/`: Contains the main proof logic
    - `proof.py`: Implements the proof generation logic
    - `__main__.py`: Entry point for the proof execution
    - `models/`: Data models for the proof system
- `demo/`: Contains sample input and output for testing
- `Dockerfile`: Defines the container image for the proof task
- `requirements.txt`: Python package dependencies

## Getting Started

To use this template:

1. Fork this repository
2. Modify the `psl_proof/proof.py` file to implement your specific proof logic
3. Update the project dependencies in `requirements.txt` if needed
4. Commit your changes and push to your repository

## Customizing the Proof Logic

The main proof logic is implemented in `psl_proof/proof.py`. To customize it, update the `Proof.generate()` function to change how input files are processed.

The proof can be configured using environment variables.

If you want to use a language other than Python, you can modify the Dockerfile to install the necessary dependencies and build the proof task in the desired language.

## Proof Scores

Loop through chat/conversal list, get average scores
1. Quality scores (qs) based on Timely, Thoughtful & Contextual
2. Uniqueness scores (us) based,
   a. For each chat, fetch the timestamp of the last entry.
   b. Determine the time difference (td) between the last entry and the current timestamp:
   c. If td > 1 hour, assign a Uniqueness Score of 1.0 for that chat, else 0.0
3. Detemine the total score (ts)
   a. if us > 0, then add value to ts.

Determine score:
   valid flag alway true
   normalise total score to value range 0 to 1
   total score is restricted by Minimum & Maximum value


## Local Development

To run the proof locally for testing, you can use Docker:

```bash
docker build -t psl-proof .
docker run \
  --rm \
  --volume $(pwd)/input:/input \
  --volume $(pwd)/output:/output \
  --env USER_EMAIL=user123@gmail.com \
  psl-proof
```

## Running with Intel TDX

Intel TDX (Trust Domain Extensions) provides hardware-based memory encryption and integrity protection for virtual machines. To run this container in a TDX-enabled environment, follow your infrastructure provider's specific instructions for deploying confidential containers.

Common volume mounts and environment variables:

```bash
docker run \
  --rm \
  --volume /path/to/input:/input \
  --volume /path/to/output:/output \
  --env USER_EMAIL=user123@gmail.com \
  psl-proof
```

Remember to populate the `/input` directory with the files you want to process.

## Security Features

This template leverages several security features:

1. **Hardware-based Isolation**: The proof runs inside a TDX-protected environment, isolating it from the rest of the system
2. **Input/Output Isolation**: Input and output directories are mounted separately, ensuring clear data flow boundaries
3. **Minimal Container**: Uses a minimal Python base image to reduce attack surface

## Contributing

If you have suggestions for improving this proof, please submit a pull request.

## License

[MIT License](LICENSE)