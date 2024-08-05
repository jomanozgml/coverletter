function onFormSubmit(e) {
    try {
        Logger.log("Form Submission Event: " + JSON.stringify(e));

        var response = e.response.getItemResponses();
        var nicNum = response[0].getResponse(); // Assuming student ID is the first question
        var submissionType = response[1].getResponse(); // Assuming submission type is the second question
        var uploaderEmail = e.response.getRespondentEmail(); // Get the email address of the respondent
        var studentName = '';
        var fileUploads = [];
        var fileType = '';
        var details = '';

        // Iterate over responses to gather all necessary data and find the multiple choice response
        for (var i = 2; i < response.length; i++) {
            var itemResponse = response[i];
            var responseType = itemResponse.getItem().getType();
            var questionTitle = itemResponse.getItem().getTitle();

            switch (responseType) {
                case FormApp.ItemType.TEXT:
                case FormApp.ItemType.PARAGRAPH_TEXT:
                    if (submissionType === 'New') {
                        if (questionTitle === 'Your full name') studentName = itemResponse.getResponse();
                        details += questionTitle + ': ' + itemResponse.getResponse() + '\n';
                     }
                    break;
                case FormApp.ItemType.FILE_UPLOAD:
                    var fileIds = itemResponse.getResponse();
                    for (var j = 0; j < fileIds.length; j++) {
                        fileUploads.push({ response: fileIds[j], title: questionTitle });
                    }
                    break;
                case FormApp.ItemType.MULTIPLE_CHOICE:
                    if (questionTitle === 'Request for') requestFor = itemResponse.getResponse();
                    else if (questionTitle === 'This is') fileType = itemResponse.getResponse();
                    break;
                default:
                    Logger.log("Unknown response type for question: " + questionTitle);
            }
        }

        if (nicNum && submissionType && uploaderEmail) {
            Logger.log(details);
            Logger.log("Uploader Email: " + uploaderEmail);

            var parentFolderId = '1IR5t3khKRe9PONFC-PCk_8whd4K5kqbU';
            var parentFolder = null;
            try {
                parentFolder = DriveApp.getFolderById(parentFolderId);
            } catch (error) {
                Logger.log("Folder with ID " + parentFolderId + " doesn't exist.");
            }

            // Create the parent folder if it doesn't exist
            if (!parentFolder) {
                parentFolder = DriveApp.getRootFolder().createFolder('Students Folder');
            }

            // Create the folder based on the multiple choice answer
            var folderName = submissionType === 'New' ? 'New' : 'Update';
            var subFolder = getOrCreateFolder(parentFolder, folderName);

            var studentFolder = getOrCreateFolder(subFolder, nicNum);

            // Check if the email file already exists
            var existingFiles = studentFolder.getFilesByName(uploaderEmail + '.txt');
            while (existingFiles.hasNext()) {
                var existingFile = existingFiles.next();
                existingFile.setTrashed(true); // Move the existing file to the trash
                Logger.log("Existing email file found and trashed: " + existingFile.getName());
            }

            // Create a new text file with the uploader's email
            var emailFile = studentFolder.createFile(uploaderEmail + '.txt', 'Uploaded by: ' + uploaderEmail);
            Logger.log("Created email text file: " + emailFile.getName());

            // Save details to a text file in the student folder
            if (submissionType === 'New')
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
                        if(submissionType === 'New')
                            var newFileName = nicNum + '-' + studentName + '-' + fileTitle;
                        else
                            var newFileName = nicNum + '-' + submissionType + '-' + fileType;

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
            Logger.log("NIC Number, submission type, or uploader email is undefined.");
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