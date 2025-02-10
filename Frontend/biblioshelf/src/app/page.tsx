"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import styles from "./page.module.css";

export default function Home() {
  const router = useRouter();

  // List of phrases to animate
  const phrases = [
    "Shhh... It's a digital library.",
    "A library you will want to get lost in.",
    "Discover books like never before.",
    "Ctrl+F, but for books.",
    "Warning: Highly Addictive Literature Inside." ,
    "Your next favorite book is just a click away."
  ];
  
  const [text, setText] = useState("");
  const [index, setIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);

  useEffect(() => {
    if (charIndex < phrases[index].length) {
      const timeout = setTimeout(() => {
        setText((prev) => prev + phrases[index][charIndex]);
        setCharIndex(charIndex + 1);
      }, 100); 

      return () => clearTimeout(timeout);
    } else {
      setTimeout(() => {
        setText("");
        setCharIndex(0);
        setIndex((prev) => (prev + 1) % phrases.length);
      }, 2000); 
    }
  }, [charIndex, index]);

  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <motion.h1 
          className={styles.title}
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
        >
          biblioshelf.
        </motion.h1>

        <p className={styles.typewriter}>{text}<span className={styles.cursor}>|</span></p>

        {/*Button */}
        <motion.button 
          className="darkbutton" 
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => router.push("/books")}
        >
          Let’s Get Started
        </motion.button>
      </main>

      <footer className={styles.footer}>
        <a
          href="https://www.gutenberg.org/"
          target="_blank"
          rel="noopener noreferrer"
        >
          Go to gutenberg.org →
        </a>
      </footer>
    </div>
  );
}
