// Toast function
function toast({ title = "", message = "", type = "info", duration = 3000 }) {
  const main = document.getElementById("toast");
  if (main) {
    const toast = document.createElement("div");

    // Auto remove toast
    const autoRemoveId = setTimeout(function () {
      main.removeChild(toast);
    }, duration + 1000);

    // Remove toast when clicked
    toast.onclick = function (e) {
      if (e.target.closest(".toast__close")) {
        main.removeChild(toast);
        clearTimeout(autoRemoveId);
      }
    };

    const icons = {
      success: "fas fa-check-circle",
      info: "fas fa-info-circle",
      warning: "fas fa-exclamation-circle",
      error: "fas fa-exclamation-circle",
    };
    const icon = icons[type];
    const delay = (duration / 1000).toFixed(2);

    toast.classList.add("toast", `toast--${type}`);
    toast.style.animation = `slideInLeft ease .3s, fadeOut linear 1s ${delay}s forwards`;

    toast.innerHTML = `
                      <div class="toast__icon">
                          <i class="${icon}"></i>
                      </div>
                      <div class="toast__body">
                          <h3 class="toast__title">${title}</h3>
                          <p class="toast__msg">${message}</p>
                      </div>
                      <div class="toast__close">
                          <i class="fas fa-times"></i>
                      </div>
                  `;
    main.appendChild(toast);
  }
}
function showSuccessToast(mesg = "Blog saved successfully!") {
  toast({
    title: "Nice!",
    message: mesg,
    type: "success",
    duration: 5000,
  });
}

function showErrorToast(mesg = "Failed to save blog. Please try again.") {
  toast({
    title: "Error!",
    message: mesg,
    type: "error",
    duration: 5000,
  });
}

function showWarning(
  mesg = "Length of the title must be less than 25 characters"
) {
  toast({
    title: "Error!",
    message: mesg,
    type: "error",
    duration: 5000,
  });
}

var blog_page = document.querySelector(".blog-page");
var create_blog_icon = document.querySelector(".nav_edit");

// Function to handle saving the blog content
function saveBlogContent(blogTitle, blogContent) {
  // Send a POST request to your Flask server to save the blog content
  fetch("/save_blog", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ blogTitle: blogTitle, blogContent: blogContent }),
  })
    .then((response) => {
      if (response.ok) {
        showSuccessToast();
        document.getElementById("blog-title").value = "";
        document.querySelector(".create-content").value = "";
      } else {
        showErrorToast();
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showErrorToast();
    });
}

// Attach an event listener to the "Create" button
document.getElementById("createButton").addEventListener("click", function () {
  // Extract the blog title from the input field
  var blogTitle = document.getElementById("blog-title").value;
    if(blogTitle.length > 25){
        showWarning();
        document.getElementById("blog-title").value = "";
        document.querySelector(".create-content").value = "";
    }else{

        // Extract the blog content from the textarea
        var blogContent = document.querySelector(".create-content").value;
        // Replace newline characters with <br> tags
        blogContent = blogContent.replace(/\n/g, '<br>');
        // Call the function to save the blog title and content
        saveBlogContent(blogTitle, blogContent);
    }
});

create_blog_icon.addEventListener("click", function () {
  if (document.querySelector(".home-page").classList.contains("none")) {
    document.querySelector(".home-page").classList.remove("none");
    blog_page.classList.add("none");
  } else {
    document.querySelector(".home-page").classList.add("none");
    blog_page.classList.remove("none");
  }
});

var noti_icon = document.querySelector(".nav_noti");
noti_icon.addEventListener("click", function () {
  if (document.querySelector(".blog-user-info").classList.contains("none")) {
    document.querySelector(".blog-user-info").classList.remove("none");
    document.querySelector(".notification").classList.add("none");
  } else if (
    !document.querySelector(".blog-user-info").classList.contains("none")
  ) {
    document.querySelector(".blog-user-info").classList.add("none");
    document.querySelector(".notification").classList.remove("none");
  }
});

document.querySelector(".nav_home").addEventListener("click", function () {
  document.querySelector(".home-page").classList.remove("none");
  blog_page.classList.add("none");
});

// Xử lí over content
var contents = document.getElementsByClassName("post-content");
for (var i = 0; i < contents.length; i++) {
  var content = contents[i].innerHTML;
  if (content.length > 104) {
    content = content.substring(0, 115) + "...";
    contents[i].innerHTML = content;
  }
}

document.querySelector(".nav_home").addEventListener("click", function () {
  document.querySelector(".home-page").classList.remove("none");
  blog_page.classList.add("none");
});

function updatePublished(blogID) {
  // Get the checkbox element based on the blog ID
  var checkbox = document.getElementById("published" + blogID);

  // Check if the checkbox is checked
  var isChecked = checkbox.checked;

  // Make AJAX request to update published status
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/update_published", true);
  xhr.setRequestHeader("Content-Type", "application/json");

  // Send the blog ID and published status in the request body
  xhr.send(JSON.stringify({ blogID: blogID, published: isChecked }));
}

// Search function
function focusInput() {
  var inputElement = document.querySelector(".input-search");
  inputElement.focus();
  document.querySelector(".menu-item-icon").classList.add("none");
}
document.querySelector(".input-search").addEventListener("blur", function () {
  document.querySelector(".menu-item-icon").classList.remove("none");
});


