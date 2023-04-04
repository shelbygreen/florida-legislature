import type { NextPage } from 'next'
import Head from 'next/head'
import Image from 'next/image'
import styles from '../styles/Home.module.css'
import Map from '../components/map'
import Link from "next/link"

const Home: NextPage = () => {
  return (
    <div className="p-1 flex flex-col min-h-screen">
    
    <div className={styles.container}>
      <Head>
        <meta name="description" content="Map of John Dailey's campaign contributions" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      {/* header */}
      <Link href="/">
        <div className=" mt-1 text-bold text-2xl text-green-900 text-left sm:text-lg sm:text-left sm:mt-1 ">Map of Florida Senate</div>
      </Link>

      {/* middle section */}
      <div className=" mt-5 text-xl text-center sm: text-lg">
          <Map/> 
      </div>

    </div>
    </div>
  )
}

export default Home