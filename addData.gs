// Google App Script
// Script to append data to Google Sheets
// GET params: chat_id, tg_login, name, phone, variants
// <Google-Sheet-Id> - Google Sheet ID to connect
function doGet(e) {
    var ss = SpreadsheetApp.openById("<Google-Sheet-Id>");
    var sheetsList = ss.getSheets();
    var sheet = sheetsList[0]
    var lastRowIndex = sheet.getLastRow().toFixed(0);
    var n = (+lastRowIndex + 1).toFixed(0);
    // Logger.log(lastRowIndex);
    // Logger.log(n);
    var range = sheet.getRange("A" + n + ":E" + n);
    range.setValues([[
        e.parameter.chat_id,
        e.parameter.tg_login,
        e.parameter.name,
        e.parameter.phone,
        e.parameter.variants,
    ]]);
}
