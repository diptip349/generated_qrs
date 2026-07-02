// Add an event listener to the form for the 'submit' event
document.getElementById('qrForm').addEventListener('submit', async function (e) {
  // Prevent the default form submission behavior (which reloads the page)
  e.preventDefault();

  // Get the form element (this will be used to gather the data)
  const form = e.target;
  
  // Create a FormData object from the form to easily send form data (including files)
  const formData = new FormData(form);

  // Show the loading message and hide other elements while waiting for the response
  document.getElementById('loadingMessage').style.display = 'block';  // Show loading spinner
  document.getElementById('qrImage').style.display = 'none';  // Hide the QR code image initially
  document.getElementById('downloadBtn').style.display = 'none';  // Hide the download button initially

  try {
    // Make an asynchronous request to the backend to generate the QR code
    const response = await fetch('/generate_qr', {
      method: 'POST',  // Using POST method for sending the form data
      body: formData  // Send the form data in the request body
    });

    // Check if the response is successful (status code in the range 200-299)
    if (!response.ok) {
      // If the response is not successful, read the error message from the server
      const errorText = await response.text();
      // Display an alert with the error message
      alert("Error generating QR:\n" + errorText);
      return;  // Exit the function to prevent further execution
    }

    // If the response is successful, get the image data as a Blob (binary data)
    const blob = await response.blob();
    
    // Create a temporary URL for the image from the Blob data
    const imageUrl = URL.createObjectURL(blob);

    // Hide the loading message once the QR code is generated
    document.getElementById('loadingMessage').style.display = 'none';
    
    // Set the 'src' of the image to the generated image URL so it is displayed
    document.getElementById('qrImage').src = imageUrl;
    
    // Show the QR code image after the data is ready
    document.getElementById('qrImage').style.display = 'block';

    // Show the download button so the user can download the QR code image
    document.getElementById('downloadBtn').style.display = 'inline-block';

    // Set up the download button functionality
    document.getElementById('downloadBtn').addEventListener('click', function() {
      // Get the selected file format from the dropdown (e.g., 'png' or 'jpg')
      const selectedFormat = document.getElementById('fileFormat').value;

      // Create a filename for the downloaded image based on the selected format
      const filename = `qr_code.${selectedFormat}`;

      // Create a temporary link element to trigger the download
      const link = document.createElement('a');
      
      // Set the 'href' of the link to the generated image URL
      link.href = imageUrl;

      // Set the 'download' attribute with the filename, so the browser will download the file
      link.download = filename;

      // Simulate a click on the link to trigger the download
      link.click();
    });

  } catch (error) {
    // If there is an error during the request or in the try block, show an error message
    alert("Error generating QR:\n" + error.message);
  }
});
