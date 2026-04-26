const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

mongoose.connect("mongodb://127.0.0.1:27017/skillchain");

const Certificate = mongoose.model("Certificate", {
  name: String,
  course: String,
  institute: String,
  certId: String,
  hash: String
});

app.post('/issue', async(req,res)=>{
   const data = new Certificate(req.body);
   await data.save();
   res.send({msg:"Certificate Issued"});
});

app.get('/verify/:id', async(req,res)=>{
   const data = await Certificate.findOne({certId:req.params.id});
   res.send(data);
});

app.listen(5000, ()=>console.log("Server Running"));