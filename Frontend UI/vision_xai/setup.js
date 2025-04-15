const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

// Check if Node.js is installed
// This function checks if Node.js is installed on the system by attempting to run the
// command node -v (which prints the Node.js version) using execSync. If the command runs
// successfully, it logs a success message and returns true. If the command fails
// (i.e., Node.js is not installed), it logs an error message and returns false.
function checkNodeInstalled() {
  try {
    execSync("node -v", { stdio: "ignore" });
    console.log("Node.js is properly installed.");
    return true;
  } catch (error) {
    console.log("Node.js is not properly installed.");
    return false;
  }
}

// Install Node.js (for Windows, macOS, or Linux)
// This function provides instructions for manual Node.js installation
function installNode() {
  console.log("Installing Node.js...");

  const platform = process.platform;
  const url =
    platform === "win32"
      ? "https://nodejs.org/dist/v18.17.1/node-v18.17.1-x64.msi"
      : "https://nodejs.org/dist/v18.17.1/node-v18.17.1.pkg";

  console.log(`Please download and install Node.js from ${url}`);
  console.log("After installing, please re-run this script.");
  process.exit(1);
}

// Check if Docker is installed
// This JavaScript function checks if Docker is installed on the system by running
// the command docker -v using execSync. If the command runs successfully, it logs
// a success message. If it fails, it logs an error message and provides a download
// link for Docker based on the system's platform (Windows, macOS, or Linux), then
// exits the script.
function checkDockerInstalled() {
  try {
    execSync("docker -v", { stdio: "ignore" });
    console.log("Docker is already installed.");
  } catch (error) {
    console.error("Docker is not installed.");

    const dockerUrl = {
      win32:
        "https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe",
      darwin: "https://desktop.docker.com/mac/stable/Docker.dmg",
      linux: "https://docs.docker.com/engine/install/",
    };

    console.log(
      `Please download and install Docker from: ${
        dockerUrl[process.platform] || dockerUrl.linux
      }`
    );
    console.log("After installing Docker, please re-run this script.");
    process.exit(1);
  }
}

// Read Flutter version from `.fvmrc`
// This JavaScript function reads the Flutter version from a file named .fvmrc
// in the current directory, parses its content as JSON, and returns the value
// of the flutter property. If the file cannot be read or parsed, it logs an
// error and exits the process.
function getFlutterVersion() {
  try {
    const fvmrcPath = path.join(__dirname, ".fvmrc");
    const fvmrcContent = fs.readFileSync(fvmrcPath, "utf-8");
    const fvmrcJson = JSON.parse(fvmrcContent);
    return fvmrcJson.flutter;
  } catch (error) {
    console.error("Error reading .fvmrc file:", error.message);
    process.exit(1);
  }
}

// Extract package name from pubspec.yaml
// This JavaScript function `extractPackageName` reads a `pubspec.yaml`
// file, extracts the package name from it, and returns the name in lowercase.
// If the file cannot be read or the package name is not found, it logs an error and exits the process.
function extractPackageName() {
  try {
    const pubspecPath = path.join(__dirname, "pubspec.yaml");
    const pubspecContent = fs.readFileSync(pubspecPath, "utf-8");

    const nameMatch = pubspecContent.match(/name:\s*(.*)/);
    if (nameMatch && nameMatch[1]) {
      // Convert to lowercase before returning
      return nameMatch[1].trim().toLowerCase();
    } else {
      console.error("Package name not found in pubspec.yaml");
      process.exit(1);
    }
  } catch (error) {
    console.error("Error reading pubspec.yaml:", error.message);
    process.exit(1);
  }
}

// Replace placeholder in Dockerfile.template and create Dockerfile
// This JavaScript function, generateDockerfile, creates a Dockerfile by replacing
// placeholders in a template file (Dockerfile.template) with a provided flutterVersion
// and the package name extracted from pubspec.yaml. It then writes the modified content
// to a new file named Dockerfile.
function generateDockerfile(flutterVersion) {
  try {
    const templatePath = path.join(__dirname, "Dockerfile.template");
    const dockerfilePath = path.join(__dirname, "Dockerfile");
    let dockerfileContent = fs.readFileSync(templatePath, "utf-8").trim();
    dockerfileContent = dockerfileContent.replace(
      "${FLUTTER_VERSION}",
      flutterVersion
    );
    dockerfileContent = dockerfileContent.replace(
      "$PACKAGE_NAME",
      extractPackageName()
    );
    fs.writeFileSync(dockerfilePath, dockerfileContent);
    console.log("Dockerfile created successfully.");
  } catch (error) {
    console.error("Error creating Dockerfile:", error.message);
    process.exit(1);
  }
}

// Function to create docker-compose.yml
function createDockerCompose() {
  const dockerComposePath = path.join(__dirname, "docker-compose.yml");

  // Check if the docker-compose.yml file already exists
  if (fs.existsSync(dockerComposePath)) {
    console.log("docker-compose.yml already exists. Skipping creation.");
    return;
  }

  // Docker Compose content
  const dockerComposeContent = `
version: '3.8'

services:
  flutter-build:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ${extractPackageName()}-container
    volumes:
      - ./build:/app/build
    ports:
      - "5000:5000"  # Expose the container's port 5000 to the host machine
    command: /bin/bash -c "
      flutter build apk --release &&
      flutter build web --release &&
      cp /output/${extractPackageName()}-release.apk /app/build/ &&
      serve -s /app/build/web -l 5000"
    # Automatically remove the container after copying the artifacts
    restart: "no"
    stop_grace_period: 30s  # Graceful stop for 30 seconds
`.trim();

  try {
    fs.writeFileSync(dockerComposePath, dockerComposeContent);
    console.log("docker-compose.yml created successfully.");
  } catch (error) {
    console.error("Error creating docker-compose.yml:", error.message);
    process.exit(1);
  }
}

// Build the Docker image
// This JavaScript function, buildDockerImage, builds a Docker image using the docker build command.
// It takes a flutterVersion parameter and passes it, along with the package name extracted from
// pubspec.yaml, as build arguments to Docker. If the build is successful, it logs a success message;
// otherwise, it logs an error message and exits the process.
function buildDockerImage(flutterVersion) {
  try {
    // Pass flutterVersion and package name to Docker as a build argument
    execSync(
      `docker build --build-arg FLUTTER_VERSION=${flutterVersion} --build-arg PACKAGE_NAME=${extractPackageName()} -t ${extractPackageName()} .`,
      { stdio: "inherit" }
    );
    console.log("Docker image built successfully.");
  } catch (error) {
    console.error("Error building Docker image:", error.message);
    process.exit(1);
  }
}

// Clean up generated Dockerfile
// This function deletes a generated Dockerfile if it exists in the current directory.
function cleanUp() {
  const dockerfilePath = path.join(__dirname, "Dockerfile");
  if (fs.existsSync(dockerfilePath)) {
    fs.unlinkSync(dockerfilePath);
    console.log("Temporary Dockerfile deleted.");
  }
}

// Main execution
(async function main() {
  if (!checkNodeInstalled()) {
    installNode();
  }

  checkDockerInstalled();

  // Get Flutter version from `.fvmrc`
  const flutterVersion = getFlutterVersion();
  console.log(`Flutter version found in .fvmrc: ${flutterVersion}`);

  generateDockerfile(flutterVersion); // Create the Dockerfile with placeholder
  // buildDockerImage(flutterVersion);    // Build Docker image with specific Flutter version
  createDockerCompose(); // Create docker-compose.yml file

  // Run 'docker-compose up --build' after creating the Dockerfile and docker-compose.yml
  try {
    execSync("docker-compose up --build", { stdio: "inherit" });
  } catch (error) {
    console.error("Error running docker-compose up:", error.message);
    console.error("Maybe you need to run docker compose up --build instead?");
    process.exit(1);
  }

  cleanUp(); // Clean up after building
})();
