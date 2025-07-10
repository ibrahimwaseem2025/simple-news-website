
document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("toggle-btn"); // Assuming the button has this ID

    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {  //add event listener to the button
            // Check if the button is showing all comments or not
            const isShowingAll = toggleBtn.getAttribute("data-showing-all") === "true";
            const newState = isShowingAll ? "false" : "true"; // Toggle the state
            
            const url = `?show_all=${newState}`;

            fetch(url, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("comment-section").innerHTML = data.html;
                toggleBtn.innerText = isShowingAll ? "Show All Comments" : "Show Less";
                toggleBtn.setAttribute("data-showing-all", (!isShowingAll).toString());
            });
        });
    }

    
});
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
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
function mySearch() {
    var x = document.getElementById("Search");
    if (x.style.display === "none") {
      x.style.display = "block";
    } else {
      x.style.display = "none";
    }
  }

  function sendReaction(reactionType) {
    const reactionsDiv = document.getElementById('reactions');
    const articleId = reactionsDiv.getAttribute('data-article-id');
    const csrfToken = reactionsDiv.getAttribute('data-csrf-token');

    fetch('/react/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
          news_id: articleId,
          reaction: reactionType
        })
      }).then(response => {
        if (response.ok) {
          window.location.reload(); // Or update counts dynamically
        } else {
          // Log the error response from the server
          response.text().then(text => {
            console.error('Server error:', text);
            alert('An error occurred: ' + text); // Show the error to the user
          });
        }
      }).catch(error => {
          console.error('Fetch error:', error);
          alert('An error occurred: ' + error);
      });
}

function sendCommentReaction(commentId, reactionType) {
  const reactionsDiv = document.getElementById('react');
  const csrfToken = reactionsDiv.getAttribute('data-csrf');
  console.log('Comment ID:', commentId); // Log the comment ID for debugging
  console.log('Reaction Type:', reactionType); // Log the reaction type for debugging

  fetch('/react_comment/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        comment_id: commentId,
        reaction: reactionType
      })
    }).then(response => {
      if (response.ok) {
        console.log('Reaction sent successfully!'); // Log success message
        console.log('Response:', response); // Log the response for debugging
        console.log('Comment ID:', commentId); // Log the comment ID for debugging
        console.log('Reaction Type:', reactionType); // Log the reaction type for debugging
        window.location.reload(); // Or update counts dynamically
      } else {
        // Log the error response from the server
        response.text().then(text => {
          console.error('Server error:', text);
          alert('An error occurred: ' + text); // Show the error to the user
        });
      }
    }).catch(error => {
        console.error('Fetch error:', error);
        alert('An error occurred: ' + error);
    });
}



