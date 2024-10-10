// payment_amountフィールドのエレメントを取得
let paymentAmountField = document.getElementById('id_payment_amount');

document.addEventListener('DOMContentLoaded', function () {
    NumberFormatter(false);

    // 保存ボタンのクリック時の処理
    document.getElementById('registerDetailButton').addEventListener('click', function (event) {
        // デフォルトのフォーム送信をキャンセル
        event.preventDefault();

        // バリデーションを実行
        if (validateForm()) {
            // 確認用モーダルを表示
            $('#saveConfirmationModal').modal('show');
        }
    });

    // 確認モーダル内のOKボタンのクリック時の処理
    document.getElementById('confirmSaveButton').addEventListener('click', function () {
        NumberFormatter(true);

        // サーバー間の保存処理を実行
        var createUrl = document.getElementById('registerDetailButton').dataset.createUrl;
        saveExpenseDetail(createUrl);
        // モーダルを閉じる
        $('#saveConfirmationModal').modal('hide');

        location.href = expenseDetailListUrl;
    });

    // 確認モーダル内のキャンセルボタンのクリック時の処理
    document.getElementById('cancelSaveButton').addEventListener('click', function () {
        // モーダルを閉じる
        $('#saveConfirmationModal').modal('hide');
    });

    // 戻るボタンのクリック時の処理
    document.getElementById('backButton').addEventListener('click', function (event) {
        // 確認用モーダルを表示
        $('#backConfirmationModal').modal('show');
    });

    // 確認モーダル内のOKボタンのクリック時の処理
    document.getElementById('confirmBackButton').addEventListener('click', function () {
        window.location.href = expenseDetailListUrl;
    });

    // 確認モーダル内のキャンセルボタンのクリック時の処理
    document.getElementById('cancelBackButton').addEventListener('click', function () {
        // モーダルを閉じる
        $('#backConfirmationModal').modal('hide');
    });

    function saveExpenseDetail(url) {
        // サーバーへの保存処理を実行
        $.ajax({
            url: url,
            type: 'POST',
            data: $('#expense-form').serialize(),
            success: function (data) {
            },
            error: function (error) {
                console.log('Error:', error);
                // エラー処理が必要な場合はここに追加
            }
        });
    }

    // 削除ボタンのクリック時の処理
    document.getElementById('deleteDetailButton').addEventListener('click', function (event) {
        // デフォルトのフォーム送信をキャンセル
        event.preventDefault();

        // 確認用モーダルを表示
        $('#deleteConfirmationModal').modal('show');
    });

    // 確認モーダル内のOKボタンのクリック時の処理
    document.getElementById('confirmDeleteButton').addEventListener('click', function () {
        // サーバー間の削除処理を実行
        var deleteUrl = document.getElementById('deleteDetailButton').dataset.deleteUrl;
        deleteExpenseDetail(deleteUrl);
        // モーダルを閉じる
        $('#deleteConfirmationModal').modal('hide');

        // リダイレクトまたは必要な処理を追加
        location.href = expenseDetailListUrl;
    });

    // 確認モーダル内のキャンセルボタンのクリック時の処理
    document.getElementById('cancelDeleteButton').addEventListener('click', function () {
        // モーダルを閉じる
        $('#deleteConfirmationModal').modal('hide');
    });

    function deleteExpenseDetail(url) {
        // サーバーへの削除処理を実行
        $.ajax({
            url: url,
            type: 'POST',  // または 'DELETE' に変更
            data: $('#expense-form').serialize(),
            success: function (data) {
                // 削除完了用モーダルを表示
                // $('#deleteCompletionModal').modal('show');
                // 削除が成功したら、リダイレクトまたは必要な処理を追加
            },
            error: function (error) {
                console.log('Error:', error);
                // エラー処理が必要な場合はここに追加
            }
        });
    }
});

function parseAndFormatNumber(value, confirmSaveFlg) {
    // カンマを除去して数値に変換
    let numericValue = parseFloat(value.replace(/,/g, ''));
    
    // 数値がNaNでないことを確認
    if (!isNaN(numericValue) && confirmSaveFlg == false){
        // カンマを付けてフォーマット
        return numericValue.toLocaleString();
    } else if (!isNaN(numericValue) && confirmSaveFlg == true) {
        // カンマを付けないフォーマット
        return numericValue;
    };

    // 数値でない場合は空文字列を返す
    return '';
}

function NumberFormatter(confirmSaveFlg) {
    // ページが読み込まれた時点での値をフォーマットして表示
    paymentAmountField.value = parseAndFormatNumber(paymentAmountField.value, confirmSaveFlg);

    // 入力内容が変更されたときのイベントリスナーを追加
    paymentAmountField.addEventListener('input', function () {
        // カンマを除去して数値に変換し、再びカンマを付けてフォーマットして表示
        paymentAmountField.value = parseAndFormatNumber(paymentAmountField.value, confirmSaveFlg);
    });
}

function validateForm() {
    let isValid = true;
    const requiredFields = document.querySelectorAll('.required-field');

    // エラーメッセージを格納するためのコンテナを取得
    const errorContainer = document.getElementById('error-container');
    errorContainer.innerHTML = '';

    requiredFields.forEach(function (field) {
        const fieldValue = field.value.trim();

        // 未入力の場合はエラーメッセージを表示
        if (!fieldValue) {
            isValid = false;
            const fieldName = field.previousElementSibling.textContent.trim();
            const errorMessage = document.createElement('p');
            errorMessage.textContent = `${fieldName}は必須項目です。`;
            errorContainer.appendChild(errorMessage);
        }
    });

    return isValid;
}