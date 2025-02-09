import { motion } from 'framer-motion';


export const Overview = () => {
  return (
    <motion.div
      key="overview"
      className="max-w-3xl mx-auto md:mt-20"
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ delay: 0.5 }}
    >
      <div className="h-screen flex items-center justify-center">
      <h1 className=" md:text-[35px] mt-40 font-nunito">
        Hi, What can I help you with?
      </h1>
    </div>
    </motion.div>
  );
};
