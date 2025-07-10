Quagga.init({
const config = {
    inputStream: {
        type: "LiveStream",
        target: document.querySelector('#camera video'),
        constraints: {
            width: { min: 640 },
            height: { min: 480 },
            facingMode: "environment"
        }
    },
    decoder: {
        readers: ["code_128_reader"]
    }
};
}, function(err) {
    if (err) {
        console.error("Ошибка инициализации QuaggaJS:", err);
        result.textContent = "Ошибка камеры";
        return;
    }
    console.log("QuaggaJS успешно инициализирован");
    Quagga.start();
});

//Quagga.init( {
//    inputStream: {
//        target: video,
//        type: "LiveStream",
//        constraints: {
//            width: { min: 640 },
//            height: { min: 480 },
//            facingMode: "environment",
//            aspectRatio: { min: 1, max: 2 }
//        },
//    },
//    decoder: {
//        readers: ["qr_code_reader"]  // Только QR-коды
//    },
//};


//Quagga.onDetected(function (data) {
//    const uuid = data.codeResult.code;
//
//    // Показываем результат
//    const resultEl = document.getElementById('result');
//    resultEl.textContent = 'Сканирование...';
//
//    // Отправляем UUID на сервер
//    fetch('/api/scan', {
//        method: 'POST',
//        headers: {
//            'Content-Type': 'application/json'
//        },
//        body: JSON.stringify({ uuid })
//    })
//    .then(res => res.json())
//    .then(json => {
//        resultEl.textContent = json.message;
//    })
//    .catch(err => {
//        console.error(err);
//        resultEl.textContent = 'Ошибка при обработке QR-кода';
//    });
//});

Quagga.onDetected(function (data) {
    const code = data.codeResult.code;

    showNotification("✅ Код распознан: " + code);

    // Отправляем на сервер
    fetch('/api/scan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ uuid: code })
    })
    .then(res => res.json())
    .then(json => {
        showNotification(json.message);
    });
});
function showNotification(message, isSuccess = null) {
    const notification = document.getElementById("notification");
    notification.textContent = message;

    if (isSuccess === true) notification.style.backgroundColor = "rgba(0, 128, 0, 0.9)";
    else if (isSuccess === false) notification.style.backgroundColor = "rgba(128, 0, 0, 0.9)";
    else notification.style.backgroundColor = "rgba(0, 0, 0, 0.8)";

    notification.style.opacity = 1;
    notification.style.pointerEvents = "auto";

    setTimeout(() => {
        notification.style.opacity = 0;
        notification.style.pointerEvents = "none";
    }, 3000);
}