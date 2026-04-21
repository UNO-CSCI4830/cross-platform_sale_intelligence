def test_check_all_fields_completed():
    email = 'timanglen@email.com'  
    first_name = "Tim"   
    last_name = "Anglen" 
    password = 'password'   
    assert email !=""
    assert first_name != ""
    assert last_name != ""
    assert password != ""


def test_missing_a_field():
    email = 'timanglen@email.com'  
    first_name = ""   
    last_name = "Anglen" 
    password = 'password'   
    assert email !=""
    assert first_name == "Tim-O'Micheal"
    assert last_name != ""
    assert password != ""


def test_check_white_spaces():
    email = 'timanglen@email.com'  
    first_name = "Tim Micheal"   
    last_name = "Anglen" 
    password = 'password'   
    assert email !=""
    assert first_name == "Tim-O'Micheal"
    assert last_name != ""
    assert password != ""


def test_check_symbols():
    email = 'timanglen@email.com'  
    first_name = "Tim-O'Micheal"   
    last_name = "Anglen" 
    password = 'password'   
    assert email !=""
    assert first_name == "Tim-O'Micheal"
    assert last_name != ""
    assert password != ""

