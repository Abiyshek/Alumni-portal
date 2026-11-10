// Shrink a photo in the browser before upload: phone photos are often 4–10 MB, over the server's 3 MB limit.
// Re-encoding as JPEG also drops EXIF metadata such as GPS location.
export async function shrinkImage(file, maxSide = 1600, quality = 0.85) {
  let bitmap;
  try {
    bitmap = await createImageBitmap(file, { imageOrientation: "from-image" });
  } catch {
    throw new Error("That photo format can't be opened here. Please choose a JPG, PNG or WEBP image.");
  }
  const scale = Math.min(1, maxSide / Math.max(bitmap.width, bitmap.height));
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(bitmap.width * scale);
  canvas.height = Math.round(bitmap.height * scale);
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#fff"; // transparent PNGs become white instead of black
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
  bitmap.close();
  const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", quality));
  if (!blob) throw new Error("Couldn't prepare that photo. Please try another one.");
  return blob;
}
