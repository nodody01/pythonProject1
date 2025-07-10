Quagga.init({
    inputStream: {
        type: "LiveStream",
        target: video,
        constraints: {
            facingMode: "environment"
        },
    },
    decoder: {
        readers: ["code_128_reader", "ean_reader", "upc_reader", "qr_code_reader"]
    }
}, function(err) {
    if (err) {
        console.error("Ошибка инициализации QuaggaJS:", err);
        result.textContent = "Ошибка камеры";
        return;
    }
    console.log("QuaggaJS успешно инициализирован");
    Quagga.start();
});