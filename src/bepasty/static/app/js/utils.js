// Show a confirm dialog box when trying to delete a file
document.getElementById("del-btn").addEventListener("click", () => {
  if(confirm("Are you sure you want to delete this file?")) {
    document.getElementById("del-frm").submit();
  }
});

// Bind click event to all line number anchor tags
document.querySelectorAll('td.linenos a').forEach(e => {
    e.addEventListener("click", function(e) {
        remove_highlights();
        var line_number = e.innerText.trim();
        highlight_line(line_number);
    })
});

// Check the value of the hash in the URL on first load
var line_number = get_hash_line_number();
if (line_number != null) {
    highlight_line(line_number);
}

// Bind the hashchange event
window.addEventListener('hashchange', function(e){
    remove_highlights();
    var line_number = get_hash_line_number();
    if (line_number != null) {
        highlight_line(line_number);
    }
});

// Highlight one line
function highlight_line(line_number) {
    var line = document.getElementById('L-' + line_number);
    line.classList.add("line-highlight");
}

// Remove highlighting from all lines
function remove_highlights() {
  document.querySelectorAll('td.code p').forEach(e =>
    e.classList.remove("line-highlight"));
}

// Get the line number from the hash if present; otherwise return null
function get_hash_line_number() {
    var type = window.location.hash;
        if (type.indexOf("-") > -1) {
            return type.split("-")[1];
        }
    return null;
}

// JS for modals, from Bulma docs: https://bulma.io/documentation/components/modal/
document.addEventListener('DOMContentLoaded', () => {
  // Functions to open and close a modal
  function openModal($el) {
    $el.classList.add('is-active');
  }

  function closeModal($el) {
    $el.classList.remove('is-active');
  }

  function closeAllModals() {
    (document.querySelectorAll('.modal') || []).forEach(($modal) => {
      closeModal($modal);
    });
  }

  // Add a click event on buttons to open a specific modal
  (document.querySelectorAll('.js-modal-trigger') || []).forEach(($trigger) => {
    const modal = $trigger.dataset.target;
    const $target = document.getElementById(modal);

    $trigger.addEventListener('click', () => {
      openModal($target);
    });
  });

  // Add a click event on various child elements to close the parent modal
  (document.querySelectorAll('.modal-background, .modal-close, .modal-card-head .delete, .modal-card-foot .button') || []).forEach(($close) => {
    const $target = $close.closest('.modal');

    $close.addEventListener('click', () => {
      closeModal($target);
    });
  });

  // Add a keyboard event to close all modals
  document.addEventListener('keydown', (event) => {
    if(event.key === "Escape") {
      closeAllModals();
    }
  });
});
