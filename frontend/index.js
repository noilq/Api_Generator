$(document).ready(function() {
    var form = $("form");
    var api_code_text = $("#api_code");
    var db_info_text = $("#db_info");

    form.on("submit", function(event) {
        event.preventDefault();
        
        var sql_code_file = $("#sql_file")[0].files[0];
        if (!sql_code_file) {
            alert("Please select a file.");
            return;
        }

        var reader = new FileReader();
        
        reader.onload = function(event) {
            var sqlCode = event.target.result;
            sendSQLFile(sqlCode);
        };

        reader.onerror = function(error) {
            console.error("File could not be read:", error);
        };

        reader.readAsText(sql_code_file);
    });

    function sendSQLFile(sqlCode) {
        var path = "http://127.0.0.1:5000/sql_code";
        
        $.ajax({
            url: path,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ sql_code: sqlCode }),
            success: function(response) {
                console.log("File sent successfully");
                console.log(response);
                console.log(response.sql_code.sql_code);
                api_code_text.text(response.api);
                db_info_text.text(JSON.stringify(response.db_info));
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("Error sending file:", textStatus, errorThrown);
            }
        });
    }
});
