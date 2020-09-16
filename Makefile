clean:
	rm -f private/dt-export/water/util/*.class

compile: 
	cd h2o-core && javac -cp ../private/dt-export/h2o.jar -d ../private/dt-export/ src/main/java/water/util/FrameUtils.java src/main/java/water/fvec/Frame.java

deploy:
	scp -r private/dt-export/water nvme:/mnt/nvme/michalk/dt-export/
