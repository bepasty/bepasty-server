function humansize (size) {
  const suffix = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"];
  let tier = 0;

  while (size >= 1024) {
    size = size / 1024;
    tier++;
  }

  return Math.round(size * 10) / 10 + " " + suffix[tier];
}

function process(fieldName, file, metadata, load, error, progress, abort, transfer, options) {
  const state = { aborted: false, xhr: null };
  let uploadUrl = null;
  let displayUrl = null;

  const controller = new AbortController();

  const doUpload = (url, name, offset) => {
    if (state.aborted) return;

    const end = Math.min(offset + MAX_BODY_SIZE, file.size);
    const xhr = new XMLHttpRequest();
    state.xhr = xhr;

    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Range", `bytes ${offset}-${end - 1}/${file.size}`);

    xhr.upload.onprogress = (e) => progress(true, offset + e.loaded, file.size);

    xhr.onload = () => {
      state.xhr = null;
      if (xhr.status < 200 || xhr.status >= 300) {
        error(`Chunk upload failed: ${xhr.status}`);
        return;
      }
      const result = JSON.parse(xhr.responseText);
      if (result.files?.[0]?.url) displayUrl = result.files[0].url;

      if (end < file.size) {
        doUpload(url, name, end);
      } else {
        load(displayUrl ?? url);
        const filesDiv = document.getElementById("files");
        const alert = document.createElement("div");
        alert.className = "notification is-success is-light";
        alert.dataset.name = name;
        const a = document.createElement("a");
        a.href = displayUrl ?? url;
        a.target = "_blank";
        a.textContent = `${file.name} (${humansize(file.size)})`;
        alert.appendChild(a);
        filesDiv.appendChild(alert);

        const fileList = document.getElementById("filelist");
        fileList.textContent += name + "\n";
        const fileListForm = document.getElementById("filelist-form");
        fileListForm.style.display = "";

        const previewBody = document.getElementById("tab-copy-preview-body");
        const inlineBody = document.getElementById("tab-copy-inline-body");
        const urlEl = document.createElement("span");
        urlEl.dataset.name = name;
        urlEl.append(window.location + name, document.createElement("br"));
        previewBody.appendChild(urlEl);
        const urlInlineEl = document.createElement("span");
        urlInlineEl.dataset.name = name;
        urlInlineEl.append(urlEl.innerText + "/+inline", document.createElement("br"));
        inlineBody.appendChild(urlInlineEl);
      }
    };

    xhr.onerror = () => { state.xhr = null; error("Network error"); };
    xhr.onabort = () => { state.xhr = null; };

    const formData = new FormData();
    formData.append("text", "");
    formData.append("contenttype", file.type || "application/octet-stream");
    formData.append("filename", file.name);
    formData.append("maxlife-value", document.querySelector("input[name=maxlife-value]").value);
    formData.append("maxlife-unit", document.querySelector("select[name=maxlife-unit]").value);
    formData.append("file", file.slice(offset, end), file.name);

    xhr.send(formData);
  };

  fetch(UPLOAD_NEW_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    signal: controller.signal,
    body: JSON.stringify({
      filename: file.name,
      size: file.size,
      type: file.type,
      maxlife_unit: document.querySelector("select[name=maxlife-unit]").value,
      maxlife_value: document.querySelector("input[name=maxlife-value]").value
    })
  })
    .then(res => {
      if (!res.ok) throw new Error("Failed to initialise upload");
      return res.json();
    })
    .then(({ name, url }) => {
      uploadUrl = url;
      doUpload(url, name, 0);
    })
    .catch(err => {
      if (err.name !== "AbortError") error(err.message);
    });

  return {
    abort: () => {
      state.aborted = true;
      controller.abort();
      if (state.xhr) state.xhr.abort();
      if (uploadUrl) fetch(`${uploadUrl}/abort`).catch(() => {});
      abort();
    }
  };
}

function revert(uniqueFileId, load, error) {
  const name = uniqueFileId.split("#")[0].slice(1)
  fetch(`/${name}/+delete`, { method: "POST" })
    .then(res => {
      if (!res.ok) throw new Error(`Delete failed: ${res.status}`);

      document.querySelectorAll(`#right-panel [data-name=${name}]`).forEach(v=>v.remove());

      const fileList = document.getElementById("filelist");
      fileList.textContent = fileList.textContent
        .split("\n")
        .filter(n => n !== name)
        .join("\n");

      if (!fileList.textContent.trim()) {
        document.getElementById("filelist-form").style.display = "none";
      }

      load();
    })
    .catch(err => error(err.message));
}

const fp = FilePond.create(document.getElementById("filepond"), {
  chunkUploads: true,
  allowMinimumUploadDuration: false,
  server: {
    fetch: null,
    revert,
    restore: null,
    load: null,
    remove: null,
    process
  }
});

document.querySelectorAll("#tab-copy-body code").forEach(el => {
  let t;
  el.addEventListener("click", async _ => {
    await navigator.clipboard.writeText(el.innerText);
    el.classList.add("copied");
    if (t) window.clearTimeout(t);
    t = setTimeout(() => {
      el.classList.remove("copied");
    }, 1500);
  });
});
