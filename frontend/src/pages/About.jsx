import React from 'react'
import { assets } from '../assets/assets'

const About = () => {
  return (
    <div>
      <div className='text-center text-2xl pt-10 text-gray-500'>
        <p>ABOUT <span className='text-gray-700 font-medium'>US</span></p>
      </div>

      <div className='my-10 flex flex-col md:flex-row gap-12'>
        <img className='w-full max-w-[360px] ' src={assets.about_image} alt="" />
        <div className='flex flex-col gap-6 justify-center md:w-2/4 text-sm text-gray-600'>
          <p>Welcome to Prescripto, Your Trusted Partner in Managing Your Healthcare Needs Conviniently And Economically At Prescripto. We Understand the Challenges Individual Face When it Comes to Scheduling Doctor's Appointment And Managing Their Health Records.</p>

          <p>Prescripto is Committed To Excellence In Healthcare Technology. We Continuously Strive To Enhance Our Platform, Integrating The Latest Advancements To Improve User Experience And Deliver Superior Service. Whether You Are Booking Your First Appointment Or Managing Ongoing Care, Prescripto is Here To Support You Every Step Of The Way.</p>

          <b className='text-gray-800'>Our Vision</b>

          <p>Our Vision At Prescripto is To Create A Seamless Healthcare Experience For Every User. We Aim To Bridge The Gap Between Patients And Healthcare Providers, Making It Easier For You TO Access The Care You Need, When You Need It.</p>
        </div>
      </div>

      <div className='text-xl my-4'>
        <p>WHY <span className='text-gray-700 font-semibold'>CHOOSE US</span></p>
      </div>

      <div className='flex flex-col md:flex-row mb-20'>
        <div className='border px-10 md:px-16 py-8 sm:py-16 flex flex-col gap-5 text-[15px] hover:bg-primary hover:text-white transition-all duration-300 text-gray-600 cursor-pointer '>
          <b>EFFICIENCY:</b>
          <p>Streamlined Appointment Scheduling That Fits Into Your Busy Lifestyle.</p>
        </div>
        <div className='border px-10 md:px-16 py-8 sm:py-16 flex flex-col gap-5 text-[15px] hover:bg-primary hover:text-white transition-all duration-300 text-gray-600 cursor-pointer '>
          <b>CONVENIENCE:</b>
          <p>Access To A Network Of Trusted Healthcare Professional in Your Area.</p>
        </div>
        <div className='border px-10 md:px-16 py-8 sm:py-16 flex flex-col gap-5 text-[15px] hover:bg-primary hover:text-white transition-all duration-300 text-gray-600 cursor-pointer '>
          <b>PERSONALIZATION:</b>
          <p>Tailored Recomendations And Remainders To Help You Stay On Top Of Your Health.</p>
        </div>
      </div>
    </div>
  )
}

export default About
