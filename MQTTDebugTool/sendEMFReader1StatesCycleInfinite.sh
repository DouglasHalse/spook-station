while true
do
	mosquitto_pub -h localhost -t "EMFReader1/use_sound" -m "false"
   for (( c=0; c<=4; c++ ))
   do 
      mosquitto_pub -h localhost -t "EMFReader1/desired_state" -m "$c"
      sleep 1
   done
done
