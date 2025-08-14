// {
//   "script": `
// let image_data = null;
// let x, y;

// const REGRESSION_FLOW = [0, 1, 1, 15, 7, 10, 11];

// // Step 1
// if (isElectron()) {
//     image_data = window.api.captureScreenshot();
// } else {
//     console.log('(Browser) Screenshot capture placeholder');
// }

// let testType = "UI Element Detection";
// let response = await detectService(testType, 0, image_data);
// x = response.x || 0;
// y = response.y || 0;
// console.log(\`Detected service at (\${x}, \${y})\`);
// performClick(0, x, y);

// // Step 2
// if (isElectron()) {
//     image_data = window.api.captureScreenshot();
// } else {
//     console.log('(Browser) Screenshot capture placeholder');
// }

// response = await detectService(testType, 1, image_data);
// x = response.x || 0;
// y = response.y || 0;
// console.log(\`Detected service at (\${x}, \${y})\`);
// performClick(0, x, y);

// // Step 3
// if (isElectron()) {
//     image_data = window.api.captureScreenshot();
// } else {
//     console.log('(Browser) Screenshot capture placeholder');
// }

// response = await detectService(testType, 1, image_data);
// x = response.x || 0;
// y = response.y || 0;
// console.log(\`Detected service at (\${x}, \${y})\`);
// performClick(0, x, y);

// // Step 4
// if (isElectron()) {
//     image_data = window.api.captureScreenshot();
// } else {
//     console.log('(Browser) Screenshot capture placeholder');
// }

// response = await detectService(testType, 15, image_data);
// x = response.x || 0;
// y = response.y || 0;
// console.log(\`Detected service at (\${x}, \${y})\`);
// performClick(0, x, y);

// // Step 5
// if (isElectron()) {
//     image_data = window.api.captureScreenshot();
// } else {
//     console.log('(Browser) Screenshot capture placeholder');
// }

// response = await detectService(testType, 7, image_data);
// x = response.x || 0;
// y = response.y || 0;
// console.log(\`Detected service at (\${x}, \${y})\`);
// performClick(0, x, y);

// // Step 6
// if (isElectron()) {
//     image_data = window.api.captureScreenshot();
// } else {
//     console.log('(Browser) Screenshot capture placeholder');
// }

// response = await detectService(testType, 10, image_data);
// x = response.x || 0;
// y = response.y || 0;
// console.log(\`Detected service at (\${x}, \${y})\`);
// performClick(0, x, y);

// // Step 7
// if (isElectron()) {
//     image_data = window.api.captureScreenshot();
// } else {
//     console.log('(Browser) Screenshot capture placeholder');
// }

// response = await detectService(testType, 11, image_data);
// x = response.x || 0;
// y = response.y || 0;
// console.log(\`Detected service at (\${x}, \${y})\`);
// performClick(0, x, y);
// `
// }





// Session Reminder : 



















