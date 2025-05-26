import React from 'react';


function Loading({ show }) {
  if (!show) return null;

  return (
    <div className="fixed top-0 left-0 right-0 bottom-0 bg-gray-500/50 flex justify-center items-center z-[999]">
      <div className="px-16 pt-8 pb-6 bg-white rounded-xl flex flex-col justify-center items-center">
        <div className="">
          <i className="animate-spin fa-solid fa-circle-notch fa-2xl" style={{ color: '#51a2ff' }}></i>
        </div>
        <div className="mt-3 font-semibold text-gray-700">Loading...</div>
      </div>
    </div>
  );
}

export default Loading;