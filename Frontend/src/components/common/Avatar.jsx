import React from "react";
import "./Avatar.css"; // Assuming you have a CSS file for styling

function Avatar({ src, alt, size }) {
  const avatarSize = size === "large" ? "avatar-large" : "avatar-small";
  return (
    <img src={src} alt={alt} className={avatarSize} />
  );
}

export default Avatar;