sound="true"

for (( i=1; i<=100; i++ ))
do 
   for (( c=0; c<=4; c++ ))
   do 
      mosquitto_pub -h localhost -t "EMFReader1/desired_state" -m "$c"
      sleep 1
   done
   sleep 0.1
   if [ $sound == "true" ];
   then
      sound="false"
   else
      sound="true"
   fi
   mosquitto_pub -h localhost -t "EMFReader1/use_sound" -m "$sound"
done
