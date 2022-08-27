	window.onload = function() {
    const iframe = document.querySelector('#cke_1_contents > iframe')
    const subjectField = document.getElementById("subject")
    console.log(iframe)


    iframe.contentWindow.document.body.addEventListener('keyup', emailBodyHandler)

    subjectField.addEventListener('keyup', emailSubjectHandler)

    let bodyPreview = document.getElementById('preview-body')

    let subjectPreview = document.getElementById('preview-subject')

    let iframeContent = iframe.contentWindow.document.body.innerHTML
    bodyPreview.innerHTML = iframeContent

    let subjectFieldContent = subjectField.value
    subjectPreview.textContent = subjectFieldContent


    function emailBodyHandler(){
        iframeContent = iframe.contentWindow.document.body.innerHTML
        bodyPreview.innerHTML = iframeContent
    }

    function emailSubjectHandler(){
        subjectFieldContent = subjectField.value
        subjectPreview.textContent = subjectFieldContent
    }
};