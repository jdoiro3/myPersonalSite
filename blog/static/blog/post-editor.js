function openForm() {
    document.getElementById("myForm").style.display = "block";
}
  
function closeForm() {
    document.getElementById("myForm").style.display = "none";
}
  
function setTextToCurrentPos() {
    let curPos = document.getElementById("markdown-editor").selectionStart;
    let content = $("#markdown-editor").val();
    let quote = $('#quote').val();
    let citation_text = $('#citation').val();
    let citation_url = $('#citation-url').val();
    if (citation_url != '') {
        var link = `<a href="${citation_url}">${citation_text}</a>`;
    } else {
        var link = `${citation_text}`;
    }
    let text_to_insert = `<blockquote>${quote}<span>${link}</span></blockquote>`;
    $("#markdown-editor").val(content.slice(0, curPos) + text_to_insert + content.slice(curPos));
    document.getElementById('content').innerHTML = marked(markdown_elem.value);
}

function slugify(text)
{
  return text.toString().toLowerCase()
    .replace(/\s+/g, '-')           // Replace spaces with -
    .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
    .replace(/\-\-+/g, '-')         // Replace multiple - with single -
    .replace(/^-+/, '')             // Trim - from start of text
    .replace(/-+$/, '');            // Trim - from end of text
}

function updateSaveAction() {
    let title = slugify(document.getElementById('title').value);
    let current_url = document.getElementById('save-changes').getAttribute('action');
    current_url = current_url.substring(0, current_url.length - 1);
    document.getElementById('save-changes').action = current_url.substring(0, current_url.lastIndexOf('/'))+`/${title}/`;
}