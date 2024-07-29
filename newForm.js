function onFormSubmit(e) {
    try {
        Logger.log("Form Submission Event: " + JSON.stringify(e));

        var response = e.response.getItemResponses();
        var orphanID = response[0].getResponse(); // Assuming orphan ID is the first question
        var motherNIC = response[1].getResponse(); // Assuming mother nic is the second question
        var guardiansPhone = response[2].getResponse(); // Assuming guardian's phone number is the third question
        var uploaderEmail = e.response.getRespondentEmail(); // Get the email address of the respondent
        var fileUploads = response.slice(3); // Get all file uploads


        if (orphanID && motherNIC && uploaderEmail) {
            if (motherNIC === 'New') {
                // Save the details in a single text file
                var details = "Orphan ID: " + orphanID + "\n" +
                    "Mother NIC: " + motherNIC + "\n" +
                    "Guardian's Phone: " + guardiansPhone + "\n" +
                    "Uploader Email: " + uploaderEmail + "\n";
                    Logger.log(details);
            }
            Logger.log("Uploader Email: " + uploaderEmail);

            var parentFolderId = '1IR5t3khKRe9PON1jUXt2uBk2VrF-dE0DZMrYwxstHbslFNr';
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

            var studentFolder = getOrCreateFolder(parentFolder, orphanID);

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
                        var newFileName = orphanID + '-' + fileTitle;

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
            Logger.log("Missing required fields: Orphan ID, Mother NIC, or Uploader Email");
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