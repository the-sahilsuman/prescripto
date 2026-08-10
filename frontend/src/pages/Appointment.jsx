import React, { useContext, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { AppContext } from '../context/AppContext'
import { assets } from '../assets/assets'
import RelatedDoctors from '../components/RelatedDoctors'
import { toast } from 'react-toastify'
import axios from 'axios'

const Appointment = () => {
  
  const {docId} =useParams()
  const {doctors ,currencysymbol, backendUrl,token, getDoctorData}= useContext(AppContext)
  const daysOfWeek =['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']

  const navigate= useNavigate()

  const [docinfo, setDocinfo] = useState(null)
  const [docslots, setDocslots]= useState([])
  const [slotindex, setSlotindex]= useState(0)
  const [slottime, setSlottime]= useState('')

  const fetchdocinfo = async ()=>{
    const docinfo= doctors.find(doc => doc._id === docId)
    setDocinfo(docinfo)
  }

  const getAvailableslot =()=>{
    if(!docinfo) return

    setDocslots([])
    // getting current date
    let today= new Date()

    for(let i=0; i<7;i++){
      // getting date with index
      let currentdate= new Date(today)
      currentdate.setDate(today.getDate()+i)
      // setting end time of the date with index

      let endtime= new Date()
      endtime.setDate(today.getDate()+i)
      endtime.setHours(21,0,0,0)

      // setting hours
      if(today.getDate()=== currentdate.getDate()){
        currentdate.setHours(currentdate.getHours()>10 ?currentdate.getHours()+1 : 10)
        currentdate.setMinutes(currentdate.getMinutes() >30 ? 30 :0)
      } else{
        currentdate.setHours(10)
        currentdate.setMilliseconds(0)
      }

      let timeslots=[]
      while(currentdate< endtime){
        let formatedtime= currentdate.toLocaleTimeString([],{hour:'2-digit', minute:'2-digit'})

        let day= currentdate.getDate()
        let month= currentdate.getMonth()+1
        let year= currentdate.getFullYear()

        const slotDate= day+'-'+month+'-'+year
        const slotTime= formatedtime

        const isSlotAvailable =docinfo.slots_booked&& docinfo.slots_booked[slotDate] && docinfo.slots_booked[slotDate].includes(slotTime) ? false: true

        if(isSlotAvailable){
          // add slots to array
          timeslots.push({
            datetime: new Date(currentdate),
            time: formatedtime
          })
        }



        // increment current time by 30 min
        currentdate.setMinutes(currentdate.getMinutes()+30)
      }

      setDocslots(prev=> ([...prev, timeslots]))
    }
  }

  const bookAppointment= async ()=>{
    if(!token){
      toast.warn('Login to book appointment')
      return navigate('/login')
    }

    try {
      
      const date= docslots[slotindex][0].datetime

      let day= date.getDate()
      let month= date.getMonth()+1
      let year= date.getFullYear()

      const slotDate= day + '-' + month + '-'+ year

      const {data}= await axios.post(backendUrl + '/api/user/book-appointment', {docId,slotDate, slotTime:slottime}, {headers:{token}})
      if(data.success){
        toast.success(data.message)
        getDoctorData()
        navigate('/my-appointments')
      } else{
        toast.error(data.message)
      }

    } catch (error) {
      console.log(error)
      toast.error(error.message)
    }

  }

  useEffect(()=>{
    fetchdocinfo()
  },[doctors,docId])

  useEffect(()=>{
    getAvailableslot()
  },[docinfo])

  useEffect(()=>{
    console.log(docslots)
  },[docslots])

  return docinfo && (
    <div>
      {/* ..doctor details.. */}
      <div className='flex flex-col sm:flex-row gap-4'>
        <div>
          <img className='bg-primary w-full sm:max-w-72 rounded-lg' src={docinfo.image} alt="" />
        </div>
        <div className='flex-1 border border-gray-400 rounded-lg px-8 py-7 bg-white mx-2 sm:mx-0 mt-[-80px] sm:mt-0'>
          {/* .. docinfo: name, degree, experience.. */}
          <p className='flex items-center gap-2 text-gray-900 text-2xl font-medium '>{docinfo.name} <img className='w-5' src={assets.verified_icon} alt="" /></p>
          <div className='flex items-center gap-2 text-sm mt-1 text-gray-600'>
            <p>{docinfo.degree} - {docinfo.speciality}</p>
            <button className='py-0.5 px-2 border text-xs rounded-full'>{docinfo.experience}</button>
          </div>
          {/* ...doctor about... */}
          <div>
            <p className='flex items-center gap-1 text-sm font-medium text-gray-900 mt-3 '>About <img src={assets.info_icon} alt="" /></p>
            <p className='text-sm text-gray-500 max-w-[700px] mt-1 '>{docinfo.about}</p>
          </div>
          <p className='text-gray-500 font-medium mt-4'>Appointment fee: <span className='text-gray-600'>{currencysymbol}{docinfo.fees}</span></p>
        </div>
      </div>
      {/* booking slots... */}
      <div className='sm:ml-72 sm:pl-4 mt-4 font-medium text-gray-700 '>
        <p>Booking Slots</p>
        <div className='flex gap-3 items-center w-full overflow-x-scroll mt-4 '>
          {
            docslots.length && docslots.map((item,index)=>(
              <div onClick={()=> setSlotindex(index)} className={`text-center py-6 min-w-16 rounded-full cursor-pointer ${slotindex=== index ? 'bg-primary text-white' : 'border border-gray-200'}`} key={index}>
                <p>{item[0] && daysOfWeek[item[0].datetime.getDay()]}</p>
                <p>{item[0] && item[0].datetime.getDate()}</p>
              </div>
            ))
          }
        </div>
        <div className='flex items-center gap-3 w-full overflow-x-scroll mt-4'>
          {docslots.length && docslots[slotindex].map((item, index)=>(
            <p onClick={()=> setSlottime(item.time)} className={`text-sm font-light flex-shrink-0 px-5 py-2 rounded-full cursor-pointer ${item.time=== slottime ? 'bg-primary text-white': 'text-gray-400 border border-b-gray-300'}`} key={index}>
              {item.time.toLowerCase()}
            </p>
          ))}
        </div>
        <button onClick={bookAppointment} className='bg-primary text-white text-sm font-light px-14 py-3 rounded-full my-6 cursor-pointer'>Book an Appointment</button>
      </div>

      {/* listing related doctors.... */}
      <RelatedDoctors docId={docId} speciality={docinfo.speciality} />
    </div>
  )
}

export default Appointment
