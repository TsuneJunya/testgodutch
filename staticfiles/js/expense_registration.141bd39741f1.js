// expense_registration.js

document.getElementById('registerButton').addEventListener('click', function (event) {
  event.preventDefault();  // フォームの通常の送信を防ぐ
  handleRegistration();
});

document.getElementById('confirmRegister').addEventListener('click', function () {
  handleRegistration();
  $('#confirmModal').modal('hide');
});

document.getElementById('deleteButton').addEventListener('click', function (event) {
    // デフォルトのフォーム送信をキャンセル
    event.preventDefault();
    // 削除ボタンがクリックされたときの処理
    $('#confirmDeleteModal').modal('show');
  });
  
document.getElementById('confirmDelete').addEventListener('click', function () {
    // 削除ボタンが確認モーダルのOKボタンでクリックされたときの処理
    var xhr = new XMLHttpRequest();
    var expense_id = document.getElementById('expense_id').value;
    xhr.open("POST", "/expense_delete_execute/" + expense_id + "/", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.onreadystatechange = function () {
      if (xhr.readyState == 4) {
        if (xhr.status == 200) {
          // サーバーからのレスポンスが成功の場合の処理
          console.log("削除が成功しました。");
          // ここに削除が成功した際の画面中央に表示するモーダルを表示する処理を追加
          $('#deleteSuccessModal').modal('show');
        } else {
          // サーバーエラーなどの場合の処理
          console.error("削除中にエラーが発生しました。");
        }
      }
    };
    xhr.send();
    $('#confirmDeleteModal').modal('hide');
  });

function handleRegistration() {
  // expense_idの値を取得
  var expense_id = document.getElementById('expense_id').value;
  
  // タイトル入力値を取得
  var titleInputValue = document.getElementById('titleInput').value;
  
  // 選択されたチェックボックスの値を取得
  var selectedCheckboxes = [];
  var checkboxElements = document.querySelectorAll('input[type="checkbox"]:checked');
  checkboxElements.forEach(function (checkbox) {
      selectedCheckboxes.push(checkbox.value);
  });

  // チェック処理
  var hasTitleError = titleInputValue.trim() === "";
  var hasCheckboxError = selectedCheckboxes.length <= 1;

  // エラーメッセージを表示・非表示
  document.getElementById('errorMessageTitle').style.display = hasTitleError ? 'block' : 'none';
  document.getElementById('errorMessageCheckbox').style.display = hasCheckboxError ? 'block' : 'none';

  // エラーがない場合、モーダルを表示
  if (!hasTitleError && !hasCheckboxError) {
      // ここでPOSTリクエストを行う
      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/expense_regist_execute/", true);
      xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
      var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
      xhr.onreadystatechange = function () {
          if (xhr.readyState == 4) {
              if (xhr.status == 200) {
                  // サーバーからのレスポンスが成功の場合の処理
                  console.log("登録が成功しました。");
                  // ここに登録が成功した際の画面中央に表示するモーダルを表示する処理を追加
                  $('#registrationSuccessModal').modal('show');
              } else {
                  // サーバーエラーなどの場合の処理
                  console.error("登録中にエラーが発生しました。");
                  var response = JSON.parse(xhr.responseText);
                  displayErrorMessage(response.message); // エラーメッセージを表示する関数を呼び出す
              }
          }
      };

      // サーバーに送信するデータを準備
      var data = {
          title: titleInputValue,
          selectedCheckboxes: selectedCheckboxes,
          expense_id: expense_id
      };

      xhr.send(JSON.stringify(data));

    // エラーメッセージを表示する関数
    function displayErrorMessage(message) {
      var errorMessageElement = document.getElementById('errorMessageServer');
      errorMessageElement.style.display = 'block';
      errorMessageElement.textContent = message;
    }
  }
}
