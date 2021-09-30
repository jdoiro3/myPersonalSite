// Django function 
// More info here: https://docs.djangoproject.com/en/3.0/ref/csrf/#ajax
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

// Slugify the post title for the server to process.
function slugify(text)
{
  return text.toString().toLowerCase()
    .replace(/\s+/g, '-')           // Replace spaces with -
    .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
    .replace(/\-\-+/g, '-')         // Replace multiple - with single -
    .replace(/^-+/, '')             // Trim - from start of text
    .replace(/-+$/, '');            // Trim - from end of text
}
  
// Adds a blockquote tag to the markdown editor.
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

// Updates the form's save action endpoint with the post's title.
// When the user inputs a title, the endpoint to save changes
// needs to be updated with the slugified version of the title.
function updateSaveAction() {
    let title = slugify(document.getElementById('title').value);
    let current_url = document.getElementById('save-changes').getAttribute('action');
    current_url = current_url.substring(0, current_url.length - 1);
    document.getElementById('save-changes').action = current_url.substring(0, current_url.lastIndexOf('/'))+`/${title}/`;
}


function addImageToUploadedModal(image) {
    let div = document.getElementById("last-row");
    let next_image_id_num = toString(parseInt(document.getElementById("last-image-id-number").value) + 1);
    div.innerHTML += `
    <div class="image-container" id="${image['id']}">
        <img class="img-fluid rounded" src='${image['url']}'>
        <a class="remove-image"><i class="fas fa-trash-alt"></i></a>
        <!-- copy the images url to the clipboard -->
        <input type="text" value="${image['url']}" id="url-${next_image_id_num}" style="display: none;">
        <div class="mytooltip" id="tooltip-${next_image_id_num}">
        <button class="toolbar-item" onclick="copyUrl('url-${next_image_id_num}', 'tooltip-${next_image_id_num}-text')" onmouseout="outFunc('tooltip-${next_image_id_num}-text')">
            <span class="tooltiptext" id="tooltip-${next_image_id_num}-text">Copy to clipboard</span>
            <i class="fas fa-link"></i>
        </button>
        </div>
    </div>
    `;
    div.querySelector(".remove-image").addEventListener("click", deleteImage);
}

function addImageToPost(image) {
    let curPos = document.getElementById("markdown-editor").selectionStart;
    let content = $("#markdown-editor").val();
    let text_to_insert = `![image](${image['url']})`;
    $("#markdown-editor").val(content.slice(0, curPos) + text_to_insert + content.slice(curPos));
    document.getElementById('content').innerHTML = marked(markdown_elem.value);
    // add the image to uploaded images modal
    addImageToUploadedModal(image);
}

function addImageHeader(image) {
    let header = document.getElementById("post-header");
    let header_image_input = document.getElementById("header-image-id");
    let image_url = image['url'];
    header.style = `background-image: url(${image_url});`
    header_image_input.value = image["id"];
}

// UPLOAD_IMAGE_ENDPOINT and USER are defined within a script tag in post-editor.html.
// This is done so that we can use Django's templating engine to dynamically define the variables.
function uploadImage(input, page_action) {
    // select your input type file and store it in a variable
    let formData = new FormData();
    formData.append('image', input.files[0]);
    formData.append('user', USER_ID);
    formData.append('post_id', POST_ID);
    // get token
    const csrftoken = getCookie('csrftoken');
    // async request without reloading the page
    fetch(UPLOAD_IMAGE_ENDPOINT, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            // we need to pass this token for Django
            'X-CSRFToken': csrftoken,
        },
        body: formData
    }).then(
        response => response.json()
    ).then(
        image_data => {
            page_action(image_data['image']);
        }
    ).catch(
        error => console.log(error)
    );
};

function deleteImage(event) {
    let image_id = event.currentTarget.parentNode.id
    // select your input type file and store it in a variable
    let formData = new FormData();
    formData.append('image_id', image_id);
    // get token
    const csrftoken = getCookie('csrftoken');
    // async request without reloading the page
    fetch(DELETE_IMAGE_ENDPOINT, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            // we need to pass this token for Django
            'X-CSRFToken': csrftoken,
        },
        body: formData
    }).then(
        response => response.json()
    ).then(
        // remove the image from the page
        image_data => {
            document.getElementById(`${image_data["image_id"]}`).remove()
        }
    ).catch(
        error => console.log(error)
    );
};

// we want the Tab key to behave correctly for the textarea used for the markdown editor
document.getElementById('markdown-editor').addEventListener('keydown', function(e) {
    if (e.key == 'Tab') {
      e.preventDefault();
      var start = this.selectionStart;
      var end = this.selectionEnd;
      // set textarea value to: text before caret + tab + text after caret
      this.value = this.value.substring(0, start) + "\t" + this.value.substring(end);
      // put caret at right position again
      this.selectionStart =
        this.selectionEnd = start + 1;
    }
  });

function copyUrl(input_id, tooltip_id) {
    var copyText = document.getElementById(input_id);
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    navigator.clipboard.writeText(copyText.value);
    var tooltip = document.getElementById(tooltip_id);
    tooltip.innerHTML = "Copied: " + copyText.value;
}
  
function outFunc(tooltip_id) {
    var tooltip = document.getElementById(tooltip_id);
    tooltip.innerHTML = "Copy to clipboard";
}

// Add event listeners
// ---------------------------------------------------------------

// Adds the functionality where a user can delete an uploaded image 
// This button lives within the Bootstrap Modal.
document.querySelectorAll(".remove-image").forEach(btn => {
    btn.addEventListener("click", deleteImage);
});

// Adds the functionality to the add image button in the toolbar. The event causes the
// file input tag to be clicked, which triggers uploadImage(this, addImageToPost) to be called.
document.getElementById("add-image-button").addEventListener('click', function(event) {
    document.getElementById('add-image-input').click();
});

// Adds the functionality to the add image header button. The effect is similar to the above.
// The click causes uploadImage(this, addImageToHeader) to be called.
document.getElementById('add-header-image').addEventListener('click', function(event) {
    document.getElementById('add-header-image-input').click();
});

// This adds the functionality to the add image button within the Bootstrap Modal.
document.getElementById('add-image-to-modal-button').addEventListener('click', function(event) {
    document.getElementById('add-image-to-modal-input').click();
});

// Select the markdown editor's content and render it into the post preview.
let markdown_elem = document.getElementById('markdown-editor');
document.getElementById('content').innerHTML = marked(markdown_elem.value);
hljs.highlightAll();

// This listens for changes in the markdown editor and renders the content
// to the post preview.
markdown_elem.addEventListener("input", (event) => {
    document.getElementById('content').innerHTML = marked(markdown_elem.value);
    hljs.highlightAll();
});

// Event listeners end
// -----------------------------------------------------