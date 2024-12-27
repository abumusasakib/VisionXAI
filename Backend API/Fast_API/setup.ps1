$ARCH = (Get-CimInstance Win32_ComputerSystem).SystemType

if ($ARCH -eq "x64-based PC") {
    $env:BASE_IMAGE = "tensorflow/tensorflow:2.8.0"
} elseif ($ARCH -eq "ARM64-based PC") {
    $env:BASE_IMAGE = "armswdev/tensorflow-arm-neoverse:r22.04-tf-2.8.0-eigen"
} else {
    Write-Host "Unsupported architecture: $ARCH"
    exit 1
}

docker-compose up --build
