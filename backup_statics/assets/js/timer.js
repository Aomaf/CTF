 // Set the date we're counting down to
 const sql = SQL.new();
 sql.open(':memory:', {
   driver: 'sqlite3'
 });
 sql.execute('SELECT * FROM table_name;');

 /*                                              
 var countDownDate = new Date("Jan 26, 2023 15:37:25").getTime();
                                                
 // Update the count down every 1 second
 var x = setInterval(function() {
 
   // Get today's date and time
   var now = new Date().getTime();
     
   // Find the distance between now and the count down date
   var distance = countDownDate - now;
     
   // Time calculations for days, hours, minutes and seconds
   var days = Math.floor(distance / (1000 * 60 * 60 * 24));
   var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
   var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
   var seconds = Math.floor((distance % (1000 * 60)) / 1000);
     
   // Output the result in an element with id="demo"
   document.getElementById("demo").innerHTML =  hours + "h "
   + minutes + "m " + seconds + "s ";
     
   // If the count down is over, write some text 
   if (distance < 0) {
     clearInterval(x);
     document.getElementById("demo").innerHTML = "EXPIRED";
   }
 }, 1000);
 */