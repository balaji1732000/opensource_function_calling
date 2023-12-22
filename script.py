

def cleanup_temp_files():
    # Define the path of the folder to clean up  
    folder_path = '/tmp'  # Change this to your temp directory
    size_threshold = 50000000  # Size threshold in bytes

    # Loop through all the files in the folder  
    for filename in os.listdir(folder_path):  
      
        # Create the file path  
        file_path = os.path.join(folder_path, filename)  
      
        # Check if it's a file
        if os.path.isfile(file_path):
            # Get the size of the file in bytes  
            file_size = os.path.getsize(file_path)  
        
            # If the file is larger than size_threshold, delete it  
            if file_size > size_threshold:  
                try:  
                    os.remove(file_path)  
                    print(f"{filename} was deleted.")  
                except Exception as e:  
                    print(f"{filename} could not be deleted. {e}")
        else:
            print(f"{filename} is not a file.")
      
    print("Disk cleanup complete.")  

# Call the function
cleanup_temp_files()
