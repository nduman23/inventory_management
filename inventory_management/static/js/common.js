const show_success = (text, cb, emmidiate = false) => {
  Toastify({
    text: text,
    duration: 3000,
    destination: "https://github.com/apvarun/toastify-js",
    newWindow: true,
    gravity: "bottom",
    position: "center",
    stopOnFocus: true,
    style: {
      color: "white",
      border: "2px",
      background: "#2b9718",
      borderRadius: "5px",
    },
  }).showToast();
  if (cb) {
    if (emmidiate) {
      cb();
    } else {
      setTimeout(cb, 2000);
    }
  }
};

const show_error = (text, cb) => {
  Toastify({
    text: text,
    duration: 3000,
    destination: "https://github.com/apvarun/toastify-js",
    newWindow: true,
    gravity: "bottom",
    position: "center",
    stopOnFocus: true,
    style: {
      color: "white",
      border: "2px",
      background: "#ed4848",
      borderRadius: "5px",
    },
  }).showToast();
  if (cb) {
    if (emmidiate) {
      cb();
    } else {
      setTimeout(cb, 2000);
    }
  }
};

const export_file = (data, name) => {
  const output = "sep=," + "\r\n\n" + data.join("\n");
  const blob = new Blob([output], { type: "text/csv" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.setAttribute("href", url);

  a.setAttribute("download", name);
  a.click();
};

const isVisible = elem => {
  return !elem?.parentElement?.classList?.contains('hidden')
}

const isValidSerialNumber = (value) => {
  return value.length == 17
}