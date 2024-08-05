function onFormSubmit(e) {
    try {
        Logger.log("Form Submission Event: " + JSON.stringify(e));

        var response = e.response.getItemResponses();
        var motherNIC = response[0].getResponse(); // Assuming orphan ID is the first question
        // var uploaderEmail = e.response.getRespondentEmail(); // Get the email address of the respondent
        var fileUploads = [];
        var details = '';

        // Iterate over responses to gather all necessary data
        for (var i = 0; i < response.length; i++) {
            var itemResponse = response[i];
            var responseType = itemResponse.getItem().getType();
            var questionTitle = itemResponse.getItem().getTitle();

            switch (responseType) {
                case FormApp.ItemType.TEXT:
                case FormApp.ItemType.PARAGRAPH_TEXT:
                case FormApp.ItemType.DATE:
                    details += questionTitle + ': ' + itemResponse.getResponse() + '\n';
                    break;
                case FormApp.ItemType.FILE_UPLOAD:
                    var fileIds = itemResponse.getResponse();
                    for (var j = 0; j < fileIds.length; j++) {
                        fileUploads.push({ response: fileIds[j], title: questionTitle });
                    }
                    break;
                default:
                    Logger.log("Unknown response type for question: " + questionTitle);
            }
        }

        if (motherNIC) {
            Logger.log(details);
            // Logger.log("Uploader Email: " + uploaderEmail);

            var parentFolderId = '1CxLSQ_VwVGHFCf_1sBIBOCyuDwA23rjk';
            var parentFolder = null;
            try {
                parentFolder = DriveApp.getFolderById(parentFolderId);
            } catch (error) {
                Logger.log("Folder with ID " + parentFolderId + " doesn't exist.");
            }

            // Create the parent folder if it doesn't exist
            if (!parentFolder) {
                parentFolder = DriveApp.getRootFolder().createFolder('Old Orphans docs');
            }
            var studentFolder = getOrCreateFolder(parentFolder, motherNIC);
            // Save details to a text file in the student folder
            studentFolder.createFile('details.txt', details);

            // Handle file uploads
            for (var i = 0; i < fileUploads.length; i++) {
                var fileId = fileUploads[i].response;
                var fileTitle = fileUploads[i].title;
                if (fileId) {
                    try {
                        Logger.log("Attempting to get file by ID: " + fileId);
                        // Get the file in Google Drive by ID
                        var file = DriveApp.getFileById(fileId);

                        // Create new file name
                        var newFileName = motherNIC + '-' + fileTitle;

                        // Move and rename the file
                        file.moveTo(studentFolder).setName(newFileName);

                        Logger.log("File moved, renamed, and uploader info stored: " + newFileName);
                    } catch (error) {
                        Logger.log("Error getting file by ID (" + fileId + "): " + error);
                    }
                } else {
                    Logger.log("File ID for upload " + (i + 1) + " is undefined.");
                }
            }
        } else {
            Logger.log("Missing required fields: Orphan ID, Mother NIC");
        }
    } catch (error) {
        Logger.log("Error: " + error);
    }
}

function getOrCreateFolder(parent, folderName) {
    var folders = parent.getFoldersByName(folderName);
    if (folders.hasNext()) {
        return folders.next();
    } else {
        return parent.createFolder(folderName);
    }
}