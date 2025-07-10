const videoElement = document.getElementById('video');
const resultElement = document.getElementById('result');

function startScanner() {
  const codeReader = new ZXing.BrowserMultiFormatReader();

  codeReader.listVideoInputDevices()
    .then(devices => {
      if (devices.length === 0) {
        resultElement.innerText = 'Камера не найдена.';
        return;
      }

      const selectedDeviceId = devices[0].deviceId;

      codeReader.decodeFromVideoDevice(selectedDeviceId, videoElement, (result, err) => {
        if (result) {
          console.log('QR найден:', result.text);
          resultElement.innerText = 'QR-код: ' + result.text;
        }
        if (err && !(err instanceof ZXing.NotFoundException)) {
          console.error('Ошибка сканирования:', err);
        }
      });
    })
    .catch(err => {
      console.error('Ошибка доступа к камере:', err);
      resultElement.innerText = 'Не удалось получить доступ к камере.';
    });
}

startScanner();