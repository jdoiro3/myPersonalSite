// Django function 
// MOre info here: https://docs.djangoproject.com/en/3.0/ref/csrf/#ajax
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function openForm(form_id) {
    document.getElementById(form_id).style.display = "block";
}
  
function closeForm(form_id) {
    document.getElementById(form_id).style.display = "none";
}
  
function addQuote() {
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

// used when a new post is being created
function updateSaveAction() {
    let title = slugify(document.getElementById('title').value);
    let current_url = document.getElementById('save-changes').getAttribute('action');
    current_url = current_url.substring(0, current_url.length - 1);
    document.getElementById('save-changes').action = current_url.substring(0, current_url.lastIndexOf('/'))+`/${title}/`;
}

document.getElementById('add-image-button').addEventListener('click', function(event) {
    document.getElementById('add-image-input').click();
} );

document.getElementById('add-header-image').addEventListener('click', function(event) {
    document.getElementById('add-header-image-input').click();
});

function addImageToPost(image) {
    let curPos = document.getElementById("markdown-editor").selectionStart;
    let content = $("#markdown-editor").val();
    let image_url = image['url'];
    let text_to_insert = `![image](${image_url})`;
    $("#markdown-editor").val(content.slice(0, curPos) + text_to_insert + content.slice(curPos));
    document.getElementById('content').innerHTML = marked(markdown_elem.value);
}

function addImageHeader(image) {
    let header = document.getElementById("post-header");
    let header_image_input = document.getElementById("header-image-id");
    let image_url = image['url'];
    header.style = `background-image: url(${image_url});`
    header_image_input.value = image["id"];
}


function uploadImage(endpoint, user, input, dom_action_func) {

    // Select your input type file and store it in a variable
    let formData = new FormData();
    formData.append('image', input.files[0]);
    formData.append('user', user);
    // get token
    const csrftoken = getCookie('csrftoken');
    console.log(input.files[0]);
    fetch(endpoint, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: formData
    }).then(
        response => response.json()
    ).then(
        image_data => {
            console.log(image_data);
            dom_action_func(image_data['image']);
        }
    ).catch(
        error => console.log(error)
    );
}