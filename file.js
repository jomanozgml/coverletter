function onFormSubmit(e) {
  try {
    Logger.log("Form Submission Event: " + JSON.stringify(e));

    var response = e.response.getItemResponses();
    var orphanId = response[0].getResponse(); // Assuming orphan ID is the first question
    var orphanType = response[1].getResponse(); // Assuming orphan type is the second question (dropdown)
    var uploaderEmail = e.response.getRespondentEmail(); // Get the email address of the respondent

    var fileUploads = response.slice(orphanType === "OLD" ? 3 : 2); // Adjust slicing based on orphan type

    if (orphanId && orphanType && uploaderEmail && fileUploads.length > 0) {
      Logger.log("Orphan ID: " + orphanId);
      Logger.log("Orphan Type: " + orphanType);
      Logger.log("Uploader Email: " + uploaderEmail);

      // Use different parent folders based on orphan type
      var parentFolderId = orphanType === "OLD" ? '1jUXt2uBk2VrF-dE0DZMrYwxstHbslFNr' : '1xQysjNHcV32wT3Eev1vAYrFP7NIMaDyg';
      var parentFolder = null;
      try {
        parentFolder = DriveApp.getFolderById(parentFolderId);
      } catch (error) {
        // Handle error if folder with given ID doesn't exist
        console.log("Folder with ID " + parentFolderId + " doesn't exist.");
      }

      // Create the parent folder if it doesn't exist
      if (!parentFolder) {
        var folderName = orphanType === "OLD" ? 'Old Orphans' : 'New Orphans';
        parentFolder = DriveApp.getRootFolder().createFolder(folderName);
      }

      var orphanFolder = getOrphanFolder(parentFolder, orphanId);

      // Check if the email file already exists
      var existingFiles = orphanFolder.getFilesByName(uploaderEmail + '.txt');
      while (existingFiles.hasNext()) {
        var existingFile = existingFiles.next();
        existingFile.setTrashed(true); // Move the existing file to the trash
        Logger.log("Existing email file found and trashed: " + existingFile.getName());
      }

      // Create a new text file with the uploader's email
      var emailFile = orphanFolder.createFile(uploaderEmail + '.txt', 'Uploaded by: ' + uploaderEmail);
      Logger.log("Created email text file: " + emailFile.getName());

      for (var i = 0; i < fileUploads.length; i++) {
        var upload = fileUploads[i];
        var fileName = orphanId + '-' + (orphanType === "OLD" ? response[2].getResponse() + '-' : '') + upload.getItem().getTitle(); // Add period only for OLD type
        var fileId = upload.getResponse();

        if (fileId) {
          try {
            Logger.log("Attempting to get file by ID: " + fileId);

            // Get the file in Google Drive by ID
            var file = DriveApp.getFileById(fileId);

            // Move and rename the file in one step
            file.moveTo(orphanFolder).setName(fileName);

            // // Transfer ownership to the uploader
            // Logger.log("Transferring ownership to: " + uploaderEmail);
            // file.setOwner(uploaderEmail);

            Logger.log("File moved, renamed, and uploader info stored: " + fileName);
          } catch (error) {
            // Handle potential error with getFileById
            Logger.log("Error getting file by ID (" + fileId + "): " + error);
            // Consider alternative file access method here (e.g., Drive API)
          }
        } else {
          Logger.log("File ID for upload " + (i + 1) + " is undefined.");
        }
      }
    } else {
      Logger.log("Orphan ID, orphan type, uploader email, or file uploads are undefined.");
    }
  } catch (error) {
    Logger.log("Error: " + error);
  }
}

// Function to get or create the orphan folder
function getOrphanFolder(parentFolder, orphanNumber) {
  var folders = parentFolder.getFoldersByName(orphanNumber);

  if (folders.hasNext()) {
    return folders.next();
  } else {
    // Create a new folder with the orphan number
    return parentFolder.createFolder(orphanNumber);
  }
}