"use client";
import styles from './page.module.css';
import { useState, useEffect } from 'react';
import axios from "axios";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import dynamic from "next/dynamic";

const Slider = dynamic(() => import("react-slick"), { ssr: false });

export default function BooksPage() {

  const DEFAULT_DOWNLOADS = 3500;


  const [searchTerm, setSearchTerm] = useState("");
  const [searchType, setSearchType] = useState("keyword"); // Default search type
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedBook, setSelectedBook] = useState({});
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [books, setBooks] = useState([])
  var [suggestedBooks, setSuggestedBooks] = useState([])

  const sliderSettings = {
    dots: true,
    infinite: true,
    speed: 800,
    slidesToShow: 5,
    slidesToScroll: 5,
    autoplay: true,
    autoplaySpeed: 3000,
    arrows: true,
  };

  useEffect(() => {
    updateRecommended()
  }, [selectedBook])


  const getImages = async (reformatedBooks) => {

    Object.entries(reformatedBooks).map(async (b) => {
      const imgsResp = await axios.get("http://localhost:5002/images/"+b[1].id)
      const imgInfo = imgsResp.data

      reformatedBooks[b[0]].imageLinks=(Object.entries(imgInfo)[0][1].imgs)
      if (Object.entries(imgInfo)[0][1].cover!=""){
      reformatedBooks[b[0]].cover=(Object.entries(imgInfo)[0][1].cover)}

    })
    setBooks(reformatedBooks)
  }

  const getImagesRec = async (reformatedBooks) => {
    const updatedBooks = await Promise.all(
      reformatedBooks.map(async (b) => {
        const imgsResp = await axios.get(`http://localhost:5002/images/${b.id}`);
        const imgInfo = imgsResp.data;

        return {
          ...b,
          imageLinks: imgInfo[Object.keys(imgInfo)[0]].imgs,
          cover: imgInfo[Object.keys(imgInfo)[0]].cover || "/default-cover.jpg",
        };
      })
    );

    setSuggestedBooks(updatedBooks);
  };


  const updateRecommended = async () => {
    if (Object.entries(selectedBook).length == 0) return;
    console.log("in update rec");

    const recResp_ = await fetch("http://localhost:5001/getRecs/" + selectedBook.id);
    const recResp = await recResp_.json().catch(({})).then(
      (resp) => {
        const recos = Object.entries(resp).map(r => ({
          id: (r[1][0]),
          title: r[1][3],
          cover: "cover",
          authors: r[1][5],
          subjects: r[1][6],
          download_count: DEFAULT_DOWNLOADS,
          description: "description"
        }));
        console.log(resp);
        console.log(recos);
        setSuggestedBooks(recos);
        getImagesRec(recos);
      }
    );
  };
  
  

  const handleSearch = async () => {
    if (!searchTerm.trim()) return; //prevent empty search
    // console.log(searchTerm)
    setLoading(true);
    setError(null);
    const url = (searchType=="regex") ? "http://localhost:5001/books/advancedSearch/" : "http://localhost:5001/books/"
    // if (searchType=="regex") {const url="http://localhost:5001/books/advancedSearch/"}
    // if (searchType=="keyword") {const url="http://localhost:5001/books/"}  

    try {
      const response = await axios.get(url+searchTerm)
      // console.log(response.data)
      // Object.entries(response.data).map(r=> {
      //   console.log(r[1][10].slice(1,-1).split(",").map(b => b.trim().slice(1,-1)))
      // })
      const reformatedBooks=Object.entries(response.data).map(r=> ({
        id: (r[1][0]),
        title: r[1][3],
        cover: "cover",
        authors: r[1][5],
        subjects: r[1][6],
        download_count: DEFAULT_DOWNLOADS,
        description: "description",
        closeness: r[1][9]
      }))
      // console.log("ok")
      // console.log(reformatedBooks)
      reformatedBooks.sort(
          (a,b) => {
            if (a.closeness<b.closeness) {
              return 1
            } else if (a.closeness>b.closeness) {
              return -1
            }
            return 0
          }
        )
      // console.log(reformatedBooks)
      setBooks(reformatedBooks)
      // updatedRecommendedBooks(reformatedBooks)
      getImages(reformatedBooks)
    } catch (err) {
      setError("Something went wrong. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <header className={styles.header}>
        <div className={styles.headerContainer}>
          <h1 className={styles.title}>biblioshelf.</h1>
          <nav>
            <a href="/" className={styles.navLink}>Home</a>
          </nav>
        </div>
      </header>
      <div className={styles.searchTitle}>
        <h2>Find Your Next Read</h2>
        <p>What are you looking for?</p>
      </div>
      {/* Search Section */}
      <div className={styles.searchSection}>
        <div className={styles.searchContainer}>
          {/* Search Type Dropdown */}
          <select
            className={styles.searchType}
            value={searchType}
            onChange={(e) => setSearchType(e.target.value)}
          >
            <option value="keyword">Keyword Search</option>
            <option value="regex">Regex Search</option>
          </select>

          {/* Search Input */}
          <input
            type="text"
            placeholder="Search books..."
            className={styles.searchInput}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />

          {/* Search Button */}
          <button className={styles.searchButton} onClick={handleSearch}>
            Search
          </button>
        </div>
      </div>

      <main>
        <div className={styles.container}>
          {/* Sidebar Filters */}
          {/*<aside className={styles.sidebar}>*/}
          {/* <div className={styles.filterGroup}>
              <label><strong>Filter by:</strong></label>
              <label>Publication Year: <strong>{publicationYear}</strong></label>
              <input type="range"
                min="1950"
                max="2023"
                value={publicationYear}
                onChange={(e) => setPublicationYear(Number(e.target.value))} />
            </div>

            <div className={styles.filterGroup}>
              <label>Number of pages <strong>{pageCount}</strong></label>
              <input type="range"
                min="1"
                max="1000"
                value={pageCount}
                onChange={(e) => setPageCount(Number(e.target.value))} />
            </div> */}

          {/*     <div className={styles.filterGroup}>
              <label>
                <strong>Number of Downloads: </strong>
                <span>{downloadCount}</span>
              </label>
              <div className={styles.rangeContainer}>
                <span className={styles.minValue}>0</span>
                <input
                  type="range"
                  min="0"
                  max="7000"
                  value={downloadCount}
                  onChange={(e) => setDownloadCount(Number(e.target.value))}
                />
                <span className={styles.maxValue}>7000</span>
              </div>
            </div>
            {/* Authors */}
          {/*<div className={styles.filterGroup}>*/}
          {/*<label>Author</label>*/}

          {/*</div>*/}

          {/* Language */}
          {/*<div className={styles.filterGroup}>
              <label>Language</label>
              <select>

              </select>

            </div>

            {/* Subject */}
          {/*<div className={styles.filterGroup}>
              <label>Subject</label>
              <select>

              </select>

            </div>

            <div className={styles.buttonContainer}>
              <button type="button" className={styles.clearButton} onClick={resetFilters}>Clear all filters</button>
            </div>*/}
          {/*</aside>*/}

          {/* Books Grid */}
          <section className={styles.mainContent}>
            {/* <div className={styles.grid}>
              {paginatedBooks.map((book) => (
                <div
                  className={styles.card}
                  key={book.id}
                  onClick={() => {
                    setSelectedBook(book);
                    updateRecommended(book);
                    setIsModalOpen(true);
                  }}
                >
                  <p>{book.title}</p>
                </div>
              ))}
            </div>*/}
            {/* Books Grid  the one with the fetch*/}
            <section className={styles.mainContent}>
              {loading && <p>Loading books...</p>}
              {error && <p className={styles.error}>{error}</p>}
              {books.length > 0 ? (
                <div className={styles.grid}>
                  {books.map((book) => (
                    <div
                      className={styles.card}
                      key={book.id}
                      onClick={() => {
                        setSelectedBook(book);
                        setIsModalOpen(true);
                        // updateRecommended();
                      }}
                    >
                      {/* <img src={book.cover || "/default-cover.jpg"} alt={`Cover of ${book.title}`} /> */}
                      <p>{book.title}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No books found. Try another search.</p>
              )}
            </section>

            {/* Pagination */}
            {/* <div className={styles.pagination}>
              {currentPage > 1 && (
                <button onClick={() => setCurrentPage(prev => prev - 1)}>
                  &larr; Previous
                </button>
              )}
              {currentPage < totalPages && (
                <button onClick={() => setCurrentPage(prev => prev + 1)}>
                  Next &rarr;
                </button>
              )}
            </div> */}
          </section>
        </div>
      </main>

      {isModalOpen && selectedBook && (
        <div className={styles.modalOverlay} onClick={() => setIsModalOpen(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <span className={styles.closeIcon} onClick={() => setIsModalOpen(false)}>&times;</span>

            {/* Main Book Details */}
            <div className={styles.modalTop}>
              <img src={selectedBook.cover} alt={`Cover of ${selectedBook.title}`} className={styles.modalImage} />
              <div className={styles.modalContent}>
                <h3>{selectedBook.title}</h3>
                <p><strong>Author: </strong>{selectedBook.authors}</p>
                <p><strong>Subjects:  </strong>{selectedBook.subjects}</p>
              </div>
            </div>

            {/* Suggested Books Carousel */}
            <div className={styles.carouselContainer}>
              <h4 className={styles.suggestedTitle}>Suggested Books</h4>
              {typeof window !== "undefined" && (
                <Slider {...sliderSettings} className={styles.carousel}>
                  {suggestedBooks.map((book) => (
                    <div key={book.id} className={styles.carouselItem} >
                      <img src={book.cover || "/default-cover.jpg"}
                        alt={`Cover of ${book.title}`}
                        className={styles.carouselImage} />
                      <p><strong>{book.title}</strong></p>
                      <p>{book.authors}</p>
                    </div>
                  ))}
                </Slider>
              )}
            </div>

          </div>
        </div>
      )}

    </>
  );
}
