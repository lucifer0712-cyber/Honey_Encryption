function login() {
    const user = document.getElementById("user").value;
    const pass = document.getElementById("pass").value;

    fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: user, password: pass })
    })
      .then(res => res.json())
      .then(data => {
        alert(data.message);

        if (data.message.includes("Incorrect")) {
          document.getElementById("login-box").classList.add("shake");
          setTimeout(() => {
            document.getElementById("login-box").classList.remove("shake");
          }, 400);
        }

        if (data.message.includes("blocked")) {
          document.getElementById("lockout-msg").classList.remove("hidden");
        }
      });
  }
